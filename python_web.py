import streamlit as st
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import pandas as pd
from collections import deque
import re
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Custom Queue Implementation for BFS (keeping original)
class Queue:
    def __init__(self, max_size=1000):
        self.queue = deque()
        self.max_size = max_size
    
    def enqueue(self, item):
        if len(self.queue) < self.max_size:
            self.queue.append(item)
            return True
        return False
    
    def dequeue(self):
        if not self.is_empty():
            return self.queue.popleft()
        return None
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def is_full(self):
        return len(self.queue) >= self.max_size
    
    def size(self):
        return len(self.queue)
    
    def front(self):
        if not self.is_empty():
            return self.queue[0]
        return None

# Web Crawler Class (keeping original functionality)
class WebCrawler:
    def __init__(self, max_urls=100, delay=1):
        self.visited_urls = set()
        self.internal_links = []
        self.external_links = []
        self.suggested_urls = []
        self.scraped_data = []
        self.max_urls = max_urls
        self.delay = delay
        self.base_domain = None
        self.crawl_stats = {
            'start_time': None,
            'end_time': None,
            'total_time': 0,
            'pages_per_second': 0
        }
    
    def is_valid_url(self, url):
        """Check if URL is valid"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme) and bool(parsed.netloc)
        except:
            return False
    
    def get_domain(self, url):
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc
        except:
            return None
    
    def fetch_page(self, url):
        """Fetch webpage content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            st.warning(f"⚠️ Error fetching {url}: {str(e)}")
            return None
    
    def extract_links(self, html_content, base_url):
        """Extract all links from HTML content"""
        links = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                
                if self.is_valid_url(full_url):
                    links.append(full_url)
        except Exception as e:
            st.error(f"❌ Error extracting links: {str(e)}")
        
        return links
    
    def crawl_bfs(self, start_url, keyword="", max_depth=2):
        """Crawl websites using BFS algorithm"""
        self.crawl_stats['start_time'] = datetime.now()
        self.base_domain = self.get_domain(start_url)
        
        # Initialize BFS queue
        url_queue = Queue(max_size=self.max_urls)
        url_queue.enqueue((start_url, 0))  # (url, depth)
        
        # Create columns for progress display
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            progress_bar = st.progress(0)
        with col2:
            progress_text = st.empty()
        with col3:
            speed_text = st.empty()
        
        status_container = st.container()
        
        crawled_count = 0
        
        while not url_queue.is_empty() and crawled_count < self.max_urls:
            current_url, depth = url_queue.dequeue()
            
            if depth > max_depth:
                continue
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            crawled_count += 1
            
            # Update progress
            progress = min(crawled_count / self.max_urls, 1.0)
            progress_bar.progress(progress)
            progress_text.metric("Progress", f"{crawled_count}/{self.max_urls}")
            
            # Calculate speed
            elapsed_time = (datetime.now() - self.crawl_stats['start_time']).total_seconds()
            if elapsed_time > 0:
                speed = crawled_count / elapsed_time
                speed_text.metric("Speed", f"{speed:.1f} pages/sec")
            
            # Show current URL being crawled
            with status_container:
                st.info(f"🔍 **Crawling:** `{current_url}` (Depth: {depth})")
            
            # Fetch page content
            html_content = self.fetch_page(current_url)
            if not html_content:
                continue
            
            # Extract links
            links = self.extract_links(html_content, current_url)
            
            for link in links:
                link_domain = self.get_domain(link)
                
                if link_domain == self.base_domain:
                    # Internal link
                    if link not in self.internal_links:
                        self.internal_links.append(link)
                        
                        # Check if link contains keyword
                        if keyword and keyword.lower() in link.lower():
                            self.suggested_urls.append(link)
                        
                        # Add to queue for further crawling
                        if link not in self.visited_urls:
                            url_queue.enqueue((link, depth + 1))
                else:
                    # External link
                    if link not in self.external_links:
                        self.external_links.append(link)
            
            # Add delay to be respectful
            time.sleep(self.delay)
        
        # Finalize stats
        self.crawl_stats['end_time'] = datetime.now()
        self.crawl_stats['total_time'] = (self.crawl_stats['end_time'] - self.crawl_stats['start_time']).total_seconds()
        self.crawl_stats['pages_per_second'] = crawled_count / self.crawl_stats['total_time'] if self.crawl_stats['total_time'] > 0 else 0
        
        progress_bar.progress(1.0)
        status_container.success(f"✅ **Crawling completed!** Found {len(self.internal_links)} internal and {len(self.external_links)} external links in {self.crawl_stats['total_time']:.1f} seconds.")
    
    def scrape_content(self, url):
        """Scrape content from a specific URL"""
        html_content = self.fetch_page(url)
        if not html_content:
            return None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title found"
            
            # Extract headings
            headings = {
                'h1': [h.get_text().strip() for h in soup.find_all('h1')],
                'h2': [h.get_text().strip() for h in soup.find_all('h2')],
                'h3': [h.get_text().strip() for h in soup.find_all('h3')]
            }
            
            # Extract paragraphs
            paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_desc.get('content', '') if meta_desc else ''
            
            return {
                'url': url,
                'title': title_text,
                'meta_description': meta_description,
                'headings': headings,
                'paragraphs': paragraphs[:5],  # First 5 paragraphs
                'total_paragraphs': len(paragraphs)
            }
        except Exception as e:
            st.error(f"❌ Error scraping {url}: {str(e)}")
            return None

def create_stats_chart(crawler):
    """Create a beautiful stats chart"""
    if not hasattr(crawler, 'internal_links'):
        return None
    
    # Create pie chart for link distribution
    labels = ['Internal Links', 'External Links', 'Suggested URLs']
    values = [len(crawler.internal_links), len(crawler.external_links), len(crawler.suggested_urls)]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        hole=.3,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=12
    )])
    
    fig.update_layout(
        title="Link Distribution",
        font=dict(size=14),
        showlegend=True,
        height=400
    )
    
    return fig

def display_advanced_metrics(crawler):
    """Display advanced metrics in a beautiful layout"""
    if not hasattr(crawler, 'crawl_stats'):
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔗 Total Links",
            value=len(crawler.internal_links) + len(crawler.external_links),
            delta=f"+{len(crawler.suggested_urls)} suggested"
        )
    
    with col2:
        st.metric(
            label="⏱️ Crawl Time",
            value=f"{crawler.crawl_stats['total_time']:.1f}s",
            delta=f"{crawler.crawl_stats['pages_per_second']:.1f} pages/sec"
        )
    
    with col3:
        st.metric(
            label="🌐 Domains Found",
            value=len(set([crawler.get_domain(url) for url in crawler.external_links if crawler.get_domain(url)])),
            delta="External domains"
        )
    
    with col4:
        st.metric(
            label="📊 Success Rate",
            value=f"{(len(crawler.internal_links) / max(len(crawler.visited_urls), 1) * 100):.1f}%",
            delta="Link extraction"
        )

# Enhanced Streamlit UI
def main():
    st.set_page_config(
        page_title="Advanced Web Crawler & Scraper",
        page_icon="🕷️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🕷️ Advanced Web Crawler & Scraper</h1>
        <p>Professional-grade web crawling with BFS algorithm and intelligent content extraction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("## ⚙️ Crawler Configuration")
        
        # Initialize session state
        if 'crawler' not in st.session_state:
            st.session_state.crawler = WebCrawler()
        
        with st.form("crawler_config"):
            start_url = st.text_input(
                "🌐 Starting URL",
                value="https://example.com",
                help="Enter the URL to start crawling from"
            )
            
            keyword = st.text_input(
                "🔍 Search Keyword",
                help="Find URLs containing this keyword"
            )
            
            st.markdown("### 📊 Crawling Parameters")
            
            max_depth = st.select_slider(
                "Maximum Depth",
                options=[1, 2, 3, 4, 5],
                value=2,
                help="How deep to crawl (1 = only starting page)"
            )
            
            max_urls = st.select_slider(
                "Maximum URLs",
                options=[10, 25, 50, 100, 150, 200],
                value=50,
                help="Limit the number of URLs to crawl"
            )
            
            delay = st.select_slider(
                "Request Delay (seconds)",
                options=[0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
                value=1.0,
                help="Be respectful to servers"
            )
            
            submitted = st.form_submit_button("🚀 Start Crawling", type="primary", use_container_width=True)
            
            if submitted:
                if not start_url:
                    st.error("Please enter a valid URL")
                else:
                    # Reset crawler
                    st.session_state.crawler = WebCrawler(max_urls=max_urls, delay=delay)
                    
                    with st.spinner("🔄 Initializing crawler..."):
                        st.session_state.crawler.crawl_bfs(start_url, keyword, max_depth)
                    
                    st.success("✅ Crawling completed!")
                    st.balloons()
        
        # Quick Actions
        st.markdown("### 🎯 Quick Actions")
        if st.button("🔄 Reset Crawler", use_container_width=True):
            st.session_state.crawler = WebCrawler()
            st.success("Crawler reset successfully!")
        
        if st.button("📊 Export All Data", use_container_width=True):
            if hasattr(st.session_state.crawler, 'internal_links'):
                # Create comprehensive export
                all_data = {
                    'internal_links': st.session_state.crawler.internal_links,
                    'external_links': st.session_state.crawler.external_links,
                    'suggested_urls': st.session_state.crawler.suggested_urls
                }
                st.download_button(
                    "📥 Download Complete Dataset",
                    data=str(all_data),
                    file_name=f"crawler_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Main Content Area
    if hasattr(st.session_state.crawler, 'internal_links') and st.session_state.crawler.internal_links:
        
        # Advanced Metrics Dashboard
        st.markdown("## 📊 Crawling Analytics")
        display_advanced_metrics(st.session_state.crawler)
        
        # Visualization
        col1, col2 = st.columns([1, 1])
        with col1:
            chart = create_stats_chart(st.session_state.crawler)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        with col2:
            # Domain analysis
            if st.session_state.crawler.external_links:
                domains = [st.session_state.crawler.get_domain(url) for url in st.session_state.crawler.external_links]
                domain_counts = pd.Series(domains).value_counts().head(10)
                
                fig_bar = px.bar(
                    x=domain_counts.values,
                    y=domain_counts.index,
                    orientation='h',
                    title="Top External Domains",
                    color=domain_counts.values,
                    color_continuous_scale="viridis"
                )
                fig_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Enhanced Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔗 Internal Links", 
            "🌐 External Links", 
            "⭐ Suggested URLs", 
            "📄 Content Scraper",
            "🔍 Advanced Analysis"
        ])
        
        with tab1:
            st.markdown("### 🔗 Internal Links Discovery")
            if st.session_state.crawler.internal_links:
                # Search functionality
                search_term = st.text_input("🔍 Search internal links:", key="internal_search")
                
                filtered_links = st.session_state.crawler.internal_links
                if search_term:
                    filtered_links = [link for link in filtered_links if search_term.lower() in link.lower()]
                
                df_internal = pd.DataFrame(filtered_links, columns=['URL'])
                df_internal['Domain'] = df_internal['URL'].apply(lambda x: urlparse(x).netloc)
                df_internal['Path Length'] = df_internal['URL'].apply(lambda x: len(urlparse(x).path))
                
                st.dataframe(
                    df_internal,
                    use_container_width=True,
                    column_config={
                        "URL": st.column_config.LinkColumn("URL"),
                        "Domain": "Domain",
                        "Path Length": st.column_config.NumberColumn("Path Length", format="%d chars")
                    }
                )
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    csv_internal = df_internal.to_csv(index=False)
                    st.download_button(
                        "📥 Download as CSV",
                        data=csv_internal,
                        file_name="internal_links.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with col2:
                    json_internal = df_internal.to_json(orient='records')
                    st.download_button(
                        "📥 Download as JSON",
                        data=json_internal,
                        file_name="internal_links.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.info("🔍 No internal links found. Try crawling a website first!")
        
        with tab2:
            st.markdown("### 🌐 External Links Analysis")
            if st.session_state.crawler.external_links:
                # Search functionality
                search_term = st.text_input("🔍 Search external links:", key="external_search")
                
                filtered_links = st.session_state.crawler.external_links
                if search_term:
                    filtered_links = [link for link in filtered_links if search_term.lower() in link.lower()]
                
                df_external = pd.DataFrame(filtered_links, columns=['URL'])
                df_external['Domain'] = df_external['URL'].apply(lambda x: urlparse(x).netloc)
                df_external['TLD'] = df_external['Domain'].apply(lambda x: x.split('.')[-1] if '.' in x else 'unknown')
                
                st.dataframe(
                    df_external,
                    use_container_width=True,
                    column_config={
                        "URL": st.column_config.LinkColumn("URL"),
                        "Domain": "Domain",
                        "TLD": "Top Level Domain"
                    }
                )
                
                # TLD Analysis
                tld_counts = df_external['TLD'].value_counts()
                if len(tld_counts) > 1:
                    fig_tld = px.pie(
                        values=tld_counts.values,
                        names=tld_counts.index,
                        title="External Links by TLD"
                    )
                    st.plotly_chart(fig_tld, use_container_width=True)
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    csv_external = df_external.to_csv(index=False)
                    st.download_button(
                        "📥 Download as CSV",
                        data=csv_external,
                        file_name="external_links.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with col2:
                    json_external = df_external.to_json(orient='records')
                    st.download_button(
                        "📥 Download as JSON",
                        data=json_external,
                        file_name="external_links.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.info("🌐 No external links found.")
        
        with tab3:
            st.markdown("### ⭐ Keyword-Matched URLs")
            if st.session_state.crawler.suggested_urls:
                df_suggested = pd.DataFrame(st.session_state.crawler.suggested_urls, columns=['URL'])
                st.dataframe(
                    df_suggested,
                    use_container_width=True,
                    column_config={
                        "URL": st.column_config.LinkColumn("URL")
                    }
                )
                
                st.success(f"Found {len(st.session_state.crawler.suggested_urls)} URLs matching your keyword!")
            else:
                st.info("⭐ No suggested URLs found. Try using a specific keyword in the crawler configuration.")
        
        with tab4:
            st.markdown("### 📄 Intelligent Content Scraper")
            
            # URL selection for scraping
            all_urls = st.session_state.crawler.internal_links + [start_url] if 'start_url' in locals() else st.session_state.crawler.internal_links
            
            if all_urls:
                selected_url = st.selectbox(
                    "🎯 Choose URL to scrape:",
                    options=all_urls,
                    help="Select a URL to extract its content"
                )
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    scrape_button = st.button("🔍 Scrape Content", type="primary", use_container_width=True)
                
                if scrape_button and selected_url:
                    with st.spinner("🔄 Extracting content..."):
                        content = st.session_state.crawler.scrape_content(selected_url)
                    
                    if content:
                        st.success("✅ Content extracted successfully!")
                        
                        # Beautiful content display
                        st.markdown("---")
                        
                        # Title and Meta
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"### 📄 {content['title']}")
                            if content['meta_description']:
                                st.markdown(f"**Meta Description:** {content['meta_description']}")
                        
                        with col2:
                            st.metric("Total Paragraphs", content['total_paragraphs'])
                        
                        # Headings Analysis
                        st.markdown("### 🏷️ Content Structure")
                        heading_cols = st.columns(3)
                        
                        for i, (heading_type, headings) in enumerate(content['headings'].items()):
                            with heading_cols[i]:
                                st.metric(f"{heading_type.upper()} Tags", len(headings))
                                if headings:
                                    with st.expander(f"View {heading_type.upper()} Content"):
                                        for heading in headings:
                                            st.write(f"• {heading}")
                        
                        # Content Preview
                        st.markdown("### 📖 Content Preview")
                        if content['paragraphs']:
                            for i, para in enumerate(content['paragraphs'], 1):
                                if para.strip():  # Only show non-empty paragraphs
                                    with st.expander(f"Paragraph {i}", expanded=(i==1)):
                                        st.write(para)
                        
                        # Export scraped content
                        st.markdown("### 📥 Export Options")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            content_json = pd.Series(content).to_json()
                            st.download_button(
                                "📄 Download as JSON",
                                data=content_json,
                                file_name=f"scraped_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        with col2:
                            # Create a simple text export
                            text_content = f"Title: {content['title']}\n\nMeta Description: {content['meta_description']}\n\nContent:\n" + "\n\n".join(content['paragraphs'])
                            st.download_button(
                                "📝 Download as Text",
                                data=text_content,
                                file_name=f"scraped_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                    else:
                        st.error("❌ Failed to scrape content from the selected URL")
            else:
                st.info("🔍 No URLs available for scraping. Please crawl a website first.")
        
        with tab5:
            st.markdown("### 🔍 Advanced Link Analysis")
            
            if st.session_state.crawler.internal_links:
                # URL pattern analysis
                st.markdown("#### 📊 URL Pattern Analysis")
                
                # Analyze URL patterns
                url_patterns = {}
                for url in st.session_state.crawler.internal_links:
                    path = urlparse(url).path
                    if path:
                        # Extract file extension or path pattern
                        if '.' in path.split('/')[-1]:
                            ext = path.split('.')[-1].lower()
                            url_patterns[f".{ext}"] = url_patterns.get(f".{ext}", 0) + 1
                        else:
                            # Count path depth
                            depth = len([p for p in path.split('/') if p])
                            url_patterns[f"depth_{depth}"] = url_patterns.get(f"depth_{depth}", 0) + 1
                
                if url_patterns:
                    pattern_df = pd.DataFrame(list(url_patterns.items()), columns=['Pattern', 'Count'])
                    fig_patterns = px.bar(
                        pattern_df,
                        x='Pattern',
                        y='Count',
                        title="URL Patterns Distribution",
                        color='Count',
                        color_continuous_scale="blues"
                    )
                    st.plotly_chart(fig_patterns, use_container_width=True)
                
                # Link depth analysis
                st.markdown("#### 🌊 Crawl Depth Analysis")
                depth_info = st.info("This shows how links were discovered at different crawling depths.")
                
                # Performance metrics
                st.markdown("#### ⚡ Performance Metrics")
                perf_col1, perf_col2, perf_col3 = st.columns(3)
                
                with perf_col1:
                    avg_links_per_page = len(st.session_state.crawler.internal_links) / max(len(st.session_state.crawler.visited_urls), 1)
                    st.metric("Avg Links/Page", f"{avg_links_per_page:.1f}")
                
                with perf_col2:
                    internal_external_ratio = len(st.session_state.crawler.internal_links) / max(len(st.session_state.crawler.external_links), 1)
                    st.metric("Internal/External Ratio", f"{internal_external_ratio:.1f}")
                
                with perf_col3:
                    if hasattr(st.session_state.crawler, 'crawl_stats'):
                        efficiency = len(st.session_state.crawler.internal_links) / max(st.session_state.crawler.crawl_stats['total_time'], 1)
                        st.metric("Links/Second", f"{efficiency:.1f}")
            else:
                st.info("🔍 No data available for analysis. Please crawl a website first.")
    
    else:
        # Welcome screen
        st.markdown("## 🚀 Welcome to Advanced Web Crawler")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🕷️ Smart Crawling
            - **BFS Algorithm** for systematic exploration
            - **Depth Control** for focused crawling
            - **Rate Limiting** for respectful crawling
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Rich Analytics
            - **Real-time Progress** tracking
            - **Visual Charts** and metrics
            - **Pattern Analysis** of discovered URLs
            """)
        
        with col3:
            st.markdown("""
            ### 🔍 Content Extraction
            - **Intelligent Scraping** of page content
            - **Structured Data** extraction
            - **Multiple Export** formats
            """)
        
        st.markdown("---")
        st.info("👈 **Get Started:** Configure your crawling parameters in the sidebar and click 'Start Crawling' to begin!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>🕷️ Advanced Web Crawler & Scraper</strong></p>
        <p>Built with ❤️ using Streamlit | Professional Web Intelligence Tool</p>
        <p>⚠️ <em>Please be respectful when crawling websites. Check robots.txt and terms of service.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
