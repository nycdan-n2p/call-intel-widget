import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';

/* Material modules */
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule   } from '@angular/material/icon';
import { MatCardModule   } from '@angular/material/card';
import { MatTableModule  } from '@angular/material/table';

/* Components */
import { AppComponent }            from './app.component';
import { AnalysisFabComponent }    from './analysis-fab.component';
import { AnalysisDialogComponent } from './analysis-dialog.component';
import { QueueFabComponent }       from './queue-fab.component';
import { QueueDialogComponent }    from './queue-dialog.component';
import { QueueChartsComponent }    from './queue-charts.component';
import { SimpleTableComponent }    from './simple-table.component';

/* Pipes */
import { MetricLabelPipe } from './metric-label.pipe';
import { DurationPipe    } from './duration.pipe';

/* Services */
import { AnalysisService } from './analysis.service';
import { QueueService }    from './queue.service';

@NgModule({
  declarations: [
    AppComponent,
    AnalysisFabComponent,
    AnalysisDialogComponent,
    QueueFabComponent,
    QueueDialogComponent,
    QueueChartsComponent,
    SimpleTableComponent,
    MetricLabelPipe,
    DurationPipe
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatTableModule
  ],
  providers: [AnalysisService, QueueService],
  bootstrap: [AppComponent]
})
export class AppModule {}