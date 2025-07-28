import { Pipe, PipeTransform } from '@angular/core';

/** "0 days 00:03:15" → "00:03:15" */
@Pipe({ name: 'hhmmss' })
export class DurationPipe implements PipeTransform {
  transform(v: string): string {
    const m = v.match(/(\d+):(\d{2}):(\d{2})$/);
    return m ? `${m[1].padStart(2, '0')}:${m[2]}:${m[3]}` : v;
  }
}