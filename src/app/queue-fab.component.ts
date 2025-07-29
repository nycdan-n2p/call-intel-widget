import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { QueueService, QueueReportJSON } from './queue.service';
import { QueueDialogComponent } from './queue-dialog.component';

@Component({
  selector: 'app-queue-fab',
  template: '<button mat-fab color="accent" class="fab" (click)="open()"><mat-icon>queue</mat-icon></button>',
  styles: ['.fab{position:fixed;bottom:24px;right:100px;z-index:1000;}']
})
export class QueueFabComponent {
  constructor(private queueService: QueueService, private dlg: MatDialog) {}
  
  open(): void {
    this.queueService.loadQueueReport().subscribe((json: QueueReportJSON) => {
      this.dlg.open(QueueDialogComponent, { width: '800px', data: json });
    });
  }
}