import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

/* ---------- typed JSON shape coming from report.json ---------- */
export interface ReportJSON {
  kpi: any;
  top_talk: any[];
  top_numbers: any[];
  top_locations: any[];
  miss_by_owner: any[];
  miss_days: any[];
  charts: { call_result: string; daily_volume: string };
  summary: string;
  mdUrl?: string;               // optional markdown download link
}

/* ---------- simple fetch wrapper ---------- */
@Injectable({ providedIn: 'root' })
export class AnalysisService {
  constructor(private http: HttpClient) {}

  /** GET the report JSON (defaults to assets folder) */
  loadReport(url = 'assets/report.json'): Observable<ReportJSON> {
    return this.http.get<ReportJSON>(url);
  }
}