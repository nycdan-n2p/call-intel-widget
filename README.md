# Analysis Widget

A comprehensive call center analytics dashboard built with Angular and Material Design that provides real-time insights into call center performance, queue analytics, and agent productivity.

## Features

### 📊 Call Analytics Dashboard
- **KPI Overview**: Track key performance indicators including total calls, answer rates, talk time, and call durations
- **Interactive Visualizations**: Charts and graphs powered by Chart.js for trend analysis
- **Executive Summary**: AI-generated insights and recommendations based on call data
- **Call Distribution Analysis**: Breakdown of inbound vs outbound calls with detailed metrics

### 📞 Queue Management Analytics
- **Service Level Monitoring**: Real-time tracking of answer rates, abandonment rates, and overflow metrics
- **Wait Time Analysis**: Average and maximum wait times with trend visualization
- **Peak Hour Identification**: Automatic detection of high-traffic periods and worst-performing time slots
- **Agent Performance Tracking**: Individual agent metrics including handle time and efficiency scores

### 🎯 Real-time Data Processing
- **CSV Data Import**: Support for net2phone Call-History CSV files
- **Python Backend Integration**: Automated report generation with `call_report.py` and `queue_analytics.py`
- **Dynamic Chart Generation**: Automatic creation of abandonment trends, hourly patterns, and agent performance charts

## Technology Stack

### Frontend
- **Angular 17**: Modern TypeScript framework with component-based architecture
- **Angular Material**: Material Design components for consistent UI/UX
- **Chart.js 4.5**: Advanced charting library for data visualization  
- **Marked**: Markdown parsing for executive summaries
- **RxJS**: Reactive programming for data streams

### Backend Processing
- **Python 3**: Data processing and report generation
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Chart and graph generation
- **OpenAI API**: AI-powered executive summary generation (optional)
- **pytz**: Timezone handling for international call data

## Project Structure

```
analysis-widget/
├── src/
│   ├── app/
│   │   ├── analysis-dialog.component.*     # Call analytics modal
│   │   ├── analysis-fab.component.ts       # Floating action button for analytics
│   │   ├── analysis.service.ts             # Call data service
│   │   ├── queue-dialog.component.*        # Queue analytics modal  
│   │   ├── queue-fab.component.ts          # Queue analytics FAB
│   │   ├── queue.service.ts                # Queue data service
│   │   ├── queue-charts.component.ts       # Chart visualization component
│   │   ├── simple-table.component.*        # Data table component
│   │   ├── duration.pipe.ts                # Time formatting pipe
│   │   └── metric-label.pipe.ts            # KPI label formatting pipe
│   ├── assets/
│   │   ├── report.json                     # Sample call analytics data
│   │   └── queue_report.json               # Sample queue analytics data
│   └── styles.css                          # Global styles
├── data/                                   # CSV data files
├── call_report.py                          # Python call analytics generator
├── queue_analytics.py                      # Python queue analytics generator
├── *.png                                   # Generated chart images
└── queue_report.md                         # Generated markdown reports
```

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ with pip
- Angular CLI 17+

### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Python Dependencies
```bash
pip install pandas matplotlib pytz phonenumbers openai
```

## Usage

### Running the Application
1. Start the Angular development server:
   ```bash
   ng serve
   ```
2. Open your browser to `http://localhost:4200`

### Data Analysis Workflow
1. **Generate Reports**: Use Python scripts to process CSV data
   ```bash
   python call_report.py your-call-data.csv
   python queue_analytics.py your-queue-data.csv
   ```

2. **View Analytics**: Click the floating action buttons in the app to view:
   - 📊 Call Analytics: Overall call center performance
   - 📞 Queue Analytics: Service level and abandonment metrics

### Key Components

#### Analysis Dialog (`analysis-dialog.component.ts:1`)
Displays comprehensive call analytics including:
- KPI metrics with Material Design icons
- Executive summary from AI analysis
- Top performers by talk time
- Call volume and efficiency metrics

#### Queue Dialog (`queue-dialog.component.ts:1`) 
Shows queue performance analytics:
- Service level indicators
- Abandonment rate tracking
- Wait time analysis
- Peak/worst period identification

#### Data Services
- **AnalysisService**: Loads call analytics from `assets/report.json`
- **QueueService**: Loads queue data from `assets/queue_report.json`

## Key Performance Indicators

### Call Analytics KPIs
- Total calls (inbound/outbound)
- Answer rate percentage
- Average call duration
- Talk time distribution
- Longest call details
- Top agents by volume

### Queue Analytics KPIs  
- Calls offered vs answered
- Abandonment rate
- Average/maximum wait times
- Service level percentage
- Peak traffic periods
- Agent efficiency scores

## Data Format

### Call Data JSON Structure
```json
{
  "kpi": {
    "total": 1211,
    "answered_pct": 82.4,
    "avg_dur": "0 days 00:00:26",
    "longest": {
      "duration": "0 days 00:29:46",
      "from_name": "Agent Name",
      "to_name": "Customer Name"
    }
  },
  "top_talk": [...],
  "summary": "Executive summary markdown..."
}
```

### Queue Data JSON Structure  
```json
{
  "queue_metrics": {
    "total_offered": 15,
    "total_answered": 9,
    "answer_rate": 60.0,
    "abandonment_rate": 40.0,
    "avg_wait_time_sec": 35,
    "peak_interval": {...}
  },
  "summary": "Queue performance summary..."
}
```

## Development

### Building Components
Components follow Angular best practices with:
- TypeScript strict mode
- Material Design principles  
- Reactive forms and observables
- Comprehensive error handling

### Adding New Metrics
1. Update the respective service (`analysis.service.ts` or `queue.service.ts`)
2. Add icon mapping in dialog components
3. Update KPI display logic
4. Extend Python report generators as needed

### Customizing Charts
Charts are generated server-side by Python scripts and displayed as images. To customize:
1. Modify `call_report.py` or `queue_analytics.py`
2. Update chart styling and data processing
3. Regenerate reports to see changes

## Production Deployment

### Build Optimization
```bash
ng build --prod
```

### Environment Configuration
Update environment files for production API endpoints and configuration.

## Contributing

This project uses:
- Angular coding standards
- Material Design guidelines
- TypeScript strict mode
- Conventional commit messages

## License

Private project for call center analytics and reporting.

---

*Generated charts and reports provide actionable insights for call center management and optimization.*