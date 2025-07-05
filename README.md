# 🕷️ WebSpy

A professional-grade web crawling and content extraction tool built with Streamlit, featuring advanced analytics, real-time progress tracking, and intelligent content scraping using the Breadth-First Search (BFS) algorithm.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## 🌟 Features

### 🚀 Core Functionality
- **Intelligent BFS Crawling**: Systematic website exploration using Breadth-First Search algorithm
- **Depth Control**: Configurable crawling depth for focused exploration
- **Rate Limiting**: Respectful crawling with customizable delays
- **Domain Filtering**: Automatic separation of internal and external links
- **Keyword Matching**: Smart URL suggestion based on keyword patterns

### 📊 Advanced Analytics
- **Real-time Progress Tracking**: Live updates with speed metrics
- **Interactive Visualizations**: Beautiful charts using Plotly
- **Performance Metrics**: Comprehensive crawling statistics
- **Pattern Analysis**: URL structure and domain distribution analysis
- **Export Capabilities**: Multiple format support (CSV, JSON, TXT)

### 🔍 Content Extraction
- **Intelligent Scraping**: Extract titles, headings, and content
- **Meta Data Extraction**: Capture meta descriptions and SEO data
- **Structured Content**: Organized heading hierarchy (H1, H2, H3)
- **Content Preview**: First 5 paragraphs with full statistics

### 🎨 Modern UI/UX
- **Professional Design**: Gradient headers and custom styling
- **Responsive Layout**: Optimized for all screen sizes
- **Interactive Components**: Enhanced forms and controls
- **Search & Filter**: Real-time link filtering capabilities
- **Progress Visualization**: Multi-metric progress tracking

## 🛠️ Installation

# Run application
streamlit run python_web.py
\`\`\`

## 📋 Requirements

Create a \`requirements.txt\` file with:
\`\`\`
streamlit>=1.28.0
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
plotly>=5.15.0
lxml>=4.9.0
\`\`\`

## 🚀 Quick Start

### Basic Usage

1. **Launch the Application**:
   \`\`\`bash
   streamlit run enhanced_web_crawler.py
   \`\`\`

2. **Configure Settings** in the sidebar:
   - Enter starting URL
   - Set optional keyword for filtering
   - Adjust crawling parameters

3. **Start Crawling** and monitor real-time progress

4. **Analyze Results** using the interactive tabs

### Configuration Options

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| **Starting URL** | Website to begin crawling | https://example.com | Any valid URL |
| **Search Keyword** | Filter URLs containing keyword | None | Any string |
| **Maximum Depth** | How deep to crawl | 2 | 1-5 levels |
| **Maximum URLs** | Limit number of URLs | 50 | 10-200 |
| **Request Delay** | Delay between requests | 1.0s | 0.5-5.0s |

## 📊 Understanding the Results

### Internal Links Tab
- **Purpose**: Shows all links within the same domain
- **Features**: Search functionality, domain analysis
- **Export**: CSV and JSON formats available

### External Links Tab
- **Purpose**: Displays links to external domains
- **Features**: TLD analysis, domain distribution
- **Analytics**: Top external domains chart

### Suggested URLs Tab
- **Purpose**: URLs matching your keyword criteria
- **Use Case**: Finding specific content or pages
- **Benefit**: Targeted link discovery

### Content Scraper Tab
- **Purpose**: Extract detailed content from any discovered URL
- **Data Extracted**:
  - Page title and meta description
  - Heading structure (H1, H2, H3)
  - Paragraph content preview
  - Content statistics

### Advanced Analysis Tab
- **URL Patterns**: File extensions and path depth analysis
- **Performance Metrics**: Crawling efficiency statistics
- **Link Ratios**: Internal vs external link distribution

## 🏗️ Architecture

### Core Components

#### 1. Queue Class
\`\`\`python
class Queue:
    # Custom BFS queue implementation
    # - Maximum size limiting
    # - FIFO operations
    # - Size tracking
\`\`\`

#### 2. WebCrawler Class
\`\`\`python
class WebCrawler:
    # Main crawling engine
    # - URL validation and processing
    # - Link extraction and categorization
    # - Content scraping capabilities
    # - Performance tracking
\`\`\`

#### 3. UI Components
- **Configuration Panel**: Sidebar settings and controls
- **Progress Tracking**: Real-time crawling updates
- **Results Display**: Tabbed interface for data exploration
- **Analytics Dashboard**: Charts and metrics visualization

### Data Flow

1. **Input**: User configures crawling parameters
2. **Processing**: BFS algorithm explores website systematically
3. **Storage**: Links categorized and stored in memory
4. **Analysis**: Real-time metrics and pattern recognition
5. **Output**: Interactive results with export capabilities

### Performance Metrics

The application tracks:
- **Crawling Speed**: Pages processed per second
- **Success Rate**: Percentage of successful page fetches
- **Link Efficiency**: Average links discovered per page
- **Memory Usage**: Real-time resource monitoring

## 🙏 Acknowledgments

- **Streamlit Team** for the amazing framework
- **BeautifulSoup** for HTML parsing capabilities
- **Plotly** for interactive visualizations
- **Requests** library for HTTP functionality



---

<div align="center">

**🕷️ Happy Crawling! 🕷️**

*Built with ❤️ for the web scraping community*

</div>

