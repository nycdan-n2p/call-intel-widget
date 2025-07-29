import { Component, Inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { marked } from 'marked';
import { QueueReportJSON } from './queue.service';

@Component({
  selector: 'app-queue-dialog',
  templateUrl: './queue-dialog.component.html',
  styleUrls: ['./queue-dialog.component.css'],
})
export class QueueDialogComponent {
  objectKeys = Object.keys;
  
  displayKpi: Record<string, string | number> = {};
  summaryHtml: SafeHtml;
  dateRange: string;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: QueueReportJSON,
    private sanitizer: DomSanitizer
  ) {
    this.displayKpi = {
      'Total Offered': data.queue_metrics.total_offered,
      'Total Answered': data.queue_metrics.total_answered,
      'Total Abandoned': data.queue_metrics.total_abandoned,
      'Answer Rate': `${data.queue_metrics.answer_rate}%`,
      'Abandonment Rate': `${data.queue_metrics.abandonment_rate}%`,
      'Avg Wait Time': `${data.queue_metrics.avg_wait_time_sec}s`,
      'Max Wait Time': `${data.queue_metrics.max_wait_time_sec}s`,
      'Avg Handle Time': `${data.queue_metrics.avg_handle_time_sec.toFixed(1)}s`
    };
    
    const html = marked.parse(data.summary || '') as string;
    this.summaryHtml = this.sanitizer.bypassSecurityTrustHtml(html);
    
    this.dateRange = this.calculateDateRange();
  }

  getKpiIcon(kpiKey: string): string {
    const iconMap: { [key: string]: string } = {
      'total offered': 'phone_in_talk',
      'total answered': 'call_received',
      'total abandoned': 'call_end',
      'answer rate': 'check_circle',
      'abandonment rate': 'cancel',
      'avg wait time': 'access_time',
      'max wait time': 'timer',
      'avg handle time': 'schedule',
      'queue': 'queue',
      'calls': 'phone',
      'rate': 'percent',
      'time': 'schedule',
      'wait': 'access_time',
      'handle': 'touch_app',
      'answered': 'call_received',
      'abandoned': 'call_end',
      'offered': 'phone_in_talk'
    };
    
    const lowerKey = kpiKey.toLowerCase();
    
    if (iconMap[lowerKey]) {
      return iconMap[lowerKey];
    }
    
    for (const [key, icon] of Object.entries(iconMap)) {
      if (lowerKey.includes(key)) {
        return icon;
      }
    }
    
    return 'insights';
  }

  private calculateDateRange(): string {
    const peakDate = new Date(this.data.queue_metrics.peak_interval.datetime);
    const worstDate = new Date(this.data.queue_metrics.worst_abandon_interval.datetime);
    
    const startDate = peakDate < worstDate ? peakDate : worstDate;
    const endDate = peakDate > worstDate ? peakDate : worstDate;
    
    const formatDate = (date: Date) => {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      });
    };
    
    if (startDate.toDateString() === endDate.toDateString()) {
      return formatDate(startDate);
    } else {
      return `${formatDate(startDate)} - ${formatDate(endDate)}`;
    }
  }
}