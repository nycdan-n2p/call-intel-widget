import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { AnalysisService, ReportJSON } from './analysis.service';
import { AnalysisDialogComponent } from './analysis-dialog.component';

@Component({
  selector: 'app-analysis-fab',
  template: '<button mat-fab color="primary" class="fab" (click)="open()"><mat-icon>analytics</mat-icon></button>',
  styles: ['.fab{position:fixed;bottom:24px;right:24px;z-index:1000;}']
})
export class AnalysisFabComponent {
  constructor(private svc: AnalysisService, private dlg: MatDialog) {}
  open(): void {
    this.svc.loadReport().subscribe((json: ReportJSON) => {
      this.dlg.open(AnalysisDialogComponent, { width: '800px', data: json });
    });
  }
}
