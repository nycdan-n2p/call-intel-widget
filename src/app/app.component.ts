import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div style="padding: 20px;">
      <h1>Analysis Widget</h1>
      <app-analysis-fab></app-analysis-fab>
      <app-queue-fab></app-queue-fab>
      <app-simple-table></app-simple-table>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = 'analysis-widget';
}