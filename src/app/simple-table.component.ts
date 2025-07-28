import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-simple-table',
  templateUrl: './simple-table.component.html',
  styleUrls: ['./simple-table.component.css']
})
export class SimpleTableComponent {
  @Input() rows: any[] = [];
  get headers(): string[] { return this.rows.length ? Object.keys(this.rows[0]) : []; }
}
