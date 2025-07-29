import { Component, Input, OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { Chart, ChartConfiguration, ChartType, registerables } from 'chart.js';
import { QueueReportJSON } from './queue.service';

Chart.register(...registerables);

@Component({
  selector: 'app-queue-charts',
  template: `
    <div class="charts-container">
      <div class="chart-section">
        <h4><mat-icon>schedule</mat-icon>Wait Time Analysis</h4>
        <canvas #waitTimeChart></canvas>
      </div>
      
      <div class="chart-section">
        <h4><mat-icon>people</mat-icon>Agent Performance</h4>
        <canvas #agentChart></canvas>
      </div>
      
      <div class="chart-section">
        <h4><mat-icon>trending_down</mat-icon>Hourly Volume vs Abandonment</h4>
        <canvas #hourlyChart></canvas>
      </div>
    </div>
  `,
  styles: [`
    .charts-container {
      display: grid;
      gap: 24px;
      margin-top: 16px;
    }
    
    .chart-section {
      background: var(--card);
      border-radius: var(--radius);
      padding: 20px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      border: 1px solid rgba(255,255,255,0.1);
    }
    
    .chart-section h4 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 16px 0;
      font-size: 1rem;
      color: var(--txt-primary);
      font-weight: 600;
    }
    
    .chart-section h4 mat-icon {
      font-size: 1.1rem;
      opacity: 0.7;
    }
    
    canvas {
      max-height: 300px;
      width: 100% !important;
    }
  `]
})
export class QueueChartsComponent implements AfterViewInit {
  @Input() data!: QueueReportJSON;
  
  @ViewChild('waitTimeChart', { static: false }) waitTimeCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('agentChart', { static: false }) agentCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('hourlyChart', { static: false }) hourlyCanvas!: ElementRef<HTMLCanvasElement>;

  ngAfterViewInit() {
    setTimeout(() => {
      this.createWaitTimeChart();
      this.createAgentChart();
      this.createHourlyChart();
    }, 100);
  }

  private createWaitTimeChart() {
    const ctx = this.waitTimeCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'bar' as ChartType,
      data: {
        labels: ['Average Wait', 'Maximum Wait'],
        datasets: [{
          label: 'Wait Time (seconds)',
          data: [
            this.data.queue_metrics.avg_wait_time_sec,
            this.data.queue_metrics.max_wait_time_sec
          ],
          backgroundColor: ['#4ade80', '#f87171'],
          borderColor: ['#22c55e', '#ef4444'],
          borderWidth: 2,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Seconds'
            }
          }
        }
      }
    };

    new Chart(ctx, config);
  }

  private createAgentChart() {
    const ctx = this.agentCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const agents = this.data.agent_performance.all_agents;
    
    const config: ChartConfiguration = {
      type: 'scatter' as ChartType,
      data: {
        datasets: [{
          label: 'Agent Performance',
          data: agents.map(agent => ({
            x: agent['ANSWERED CALLS'],
            y: agent.EFFICIENCY
          })),
          backgroundColor: '#3b82f6',
          borderColor: '#1d4ed8',
          borderWidth: 2,
          pointRadius: 8,
          pointHoverRadius: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const agent = agents[context.dataIndex];
                return `${agent.AGENT}: ${context.parsed.x} calls, ${context.parsed.y.toFixed(2)} efficiency`;
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Calls Answered'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Efficiency Rating'
            }
          }
        }
      }
    };

    new Chart(ctx, config);
  }

  private createHourlyChart() {
    const ctx = this.hourlyCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const hourlyData = this.data.service_trends.sort((a, b) => a.HOUR - b.HOUR);
    
    const config: ChartConfiguration = {
      type: 'line' as ChartType,
      data: {
        labels: hourlyData.map(h => `${h.HOUR}:00`),
        datasets: [
          {
            label: 'Total Calls',
            data: hourlyData.map(h => h.TOTAL_OFFERED),
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            yAxisID: 'y',
            tension: 0.4
          },
          {
            label: 'Abandonment Rate (%)',
            data: hourlyData.map(h => h.ABANDONMENT_RATE),
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            yAxisID: 'y1',
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index' as const,
          intersect: false,
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Hour of Day'
            }
          },
          y: {
            type: 'linear' as const,
            display: true,
            position: 'left' as const,
            title: {
              display: true,
              text: 'Total Calls'
            }
          },
          y1: {
            type: 'linear' as const,
            display: true,
            position: 'right' as const,
            title: {
              display: true,
              text: 'Abandonment Rate (%)'
            },
            grid: {
              drawOnChartArea: false,
            },
          }
        }
      }
    };

    new Chart(ctx, config);
  }
}