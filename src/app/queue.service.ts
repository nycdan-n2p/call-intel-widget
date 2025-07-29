import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface QueueReportJSON {
  queue_name?: string;
  queue_metrics: {
    total_offered: string;
    total_answered: string;
    total_abandoned: string;
    total_overflowed: string;
    abandonment_rate: number;
    answer_rate: number;
    overflow_rate: number;
    avg_wait_time_sec: number;
    max_wait_time_sec: number;
    avg_handle_time_sec: number;
    peak_interval: {
      datetime: string;
      answered_calls: string;
      abandoned_calls: string;
    };
    worst_abandon_interval: {
      datetime: string;
      abandoned_calls: string;
      answered_calls: string;
    };
  };
  service_trends: Array<{
    HOUR: number;
    'ANSWERED CALLS': number;
    'ABANDONED CALLS': number;
    'OVERFLOWED CALLS': number;
    TOTAL_OFFERED: number;
    ABANDONMENT_RATE: number;
  }>;
  agent_performance: {
    all_agents: Array<{
      AGENT: string;
      'ANSWERED CALLS': number;
      TOTAL_HANDLE_SEC: number;
      AVG_HANDLE_SEC: number;
      MAX_HANDLE_SEC: number;
      AVG_HANDLE_TIME: number;
      EFFICIENCY: number;
    }>;
    top_volume: Array<{
      AGENT: string;
      'ANSWERED CALLS': number;
      AVG_HANDLE_TIME: number;
    }>;
    most_efficient: Array<{
      AGENT: string;
      'ANSWERED CALLS': number;
      EFFICIENCY: number;
      AVG_HANDLE_TIME: number;
    }>;
  };
  charts: {
    abandonment: string;
    hourly: string;
    agents: string;
  };
  summary: string;
}

@Injectable({ providedIn: 'root' })
export class QueueService {
  constructor(private http: HttpClient) {}

  loadQueueReport(url = 'assets/queue_report.json'): Observable<QueueReportJSON> {
    return this.http.get<QueueReportJSON>(url);
  }
}