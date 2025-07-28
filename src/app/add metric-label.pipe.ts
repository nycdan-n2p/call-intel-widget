import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'metricLabel' })
export class MetricLabelPipe implements PipeTransform {
  private map: Record<string, string> = {
    total: 'Total', inbound: 'Inbound', outbound: 'Outbound',
    answered_pct: 'Answered %', missed_pct: 'Missed %',
    vm_pct: 'VM %', blocked_pct: 'Blocked %',
    avg_dur: 'Avg', median_dur: 'Median',
    talk_time: 'Talk', longest: 'Longest',
  };
  transform(key: string): string { return this.map[key] ?? key; }
}