import { Component, Inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { marked } from 'marked';
import { ReportJSON } from './analysis.service';

@Component({
  selector: 'app-analysis-dialog',
  templateUrl: './analysis-dialog.component.html',
  styleUrls: ['./analysis-dialog.component.css'],
})
export class AnalysisDialogComponent {
  objectKeys = Object.keys;
  
  /** KPI map with "longest" flattened into a readable string */
  displayKpi: Record<string, string | number> = {};
  
  /** Trusted HTML version of the executive-summary Markdown */
  summaryHtml: SafeHtml;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: ReportJSON,
    private sanitizer: DomSanitizer
  ) {
    /*  1 — build friendly KPI map */
    this.displayKpi = { ...data.kpi };
    if (typeof data.kpi.longest === 'object' && data.kpi.longest) {
      const l = data.kpi.longest;
      this.displayKpi['longest'] = `${l.duration} (${l.from_name} → ${l.to_name})`;
    }
    
    /*  2 — convert Markdown → HTML and mark it safe */
    const html = marked.parse(data.summary || '') as string;  // cast to string to satisfy TS
    this.summaryHtml = this.sanitizer.bypassSecurityTrustHtml(html);
  }

  /**
   * Returns appropriate Material icon name based on KPI key
   */
  getKpiIcon(kpiKey: string): string {
    const iconMap: { [key: string]: string } = {
      'calls': 'phone',
      'duration': 'schedule',
      'success': 'check_circle',
      'missed': 'phone_missed',
      'answered': 'call_received',
      'outbound': 'call_made',
      'inbound': 'call_received',
      'average': 'trending_up',
      'total': 'analytics',
      'rate': 'percent',
      'volume': 'volume_up',
      'longest': 'timer',
      'shortest': 'timer_off',
      'failed': 'error',
      'busy': 'phone_busy',
      'voicemail': 'voicemail',
      'transfer': 'call_split',
      'hold': 'pause_circle',
      'queue': 'queue',
      'agent': 'person',
      'customer': 'people',
      'satisfaction': 'sentiment_satisfied',
      'resolution': 'task_alt',
      'escalation': 'trending_up',
      'abandoned': 'call_end',
      'wait': 'access_time',
      'response': 'reply'
    };
    
    // Find the best matching icon based on key content
    const lowerKey = kpiKey.toLowerCase();
    
    // Direct match first
    if (iconMap[lowerKey]) {
      return iconMap[lowerKey];
    }
    
    // Partial match
    for (const [key, icon] of Object.entries(iconMap)) {
      if (lowerKey.includes(key)) {
        return icon;
      }
    }
    
    return 'insights'; // default icon
  }
}