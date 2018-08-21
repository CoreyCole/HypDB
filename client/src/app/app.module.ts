import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

// angular material components
import {
  MatButtonModule,
  MatCheckboxModule,
  MatToolbarModule,
  MatGridListModule,
  MatTabsModule,
  MatCardModule,
  MatListModule,
  MatSlideToggleModule,
  MatSidenavModule,
  MatInputModule,
  MatFormFieldModule,
  MatSelectModule,
  MatChipsModule,
  MatProgressSpinnerModule,
  MatProgressBarModule,
  MatAutocompleteModule,
  MatOptionModule
} from '@angular/material';
import 'hammerjs';

// ngx charts
import { NgxChartsModule, BarChartModule } from '@swimlane/ngx-charts';

// ngx dag
import { NgxGraphModule } from '@swimlane/ngx-graph';

// csv parser
import { PapaParseModule } from 'ngx-papaparse';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomePageComponent } from './pages/home-page/home-page.component';
import { MainService } from './services/main.service';
import { BarChartDemoComponent } from './components/bar-chart-demo/bar-chart-demo.component';
import { CsvUploadComponent } from './components/csv-upload/csv-upload.component';
import { QueryComponent } from './components/query/query.component';
import { PickParamsComponent } from './components/query/pick-params/pick-params.component';
import { DagDemoComponent } from './components/dag-demo/dag-demo.component';
import { GroupByChartsComponent } from './components/group-by-charts/group-by-charts.component';
import { GraphComponent } from './components/graph/graph.component';
import { UploadCsvPageComponent } from './pages/upload-csv-page/upload-csv-page.component';
import { NaiveGroupByChartComponent } from './components/naive-group-by-chart/naive-group-by-chart.component';

@NgModule({
  declarations: [
    AppComponent,
    // pages
    HomePageComponent,
    UploadCsvPageComponent,
    // components
    BarChartDemoComponent,
    CsvUploadComponent,
    QueryComponent,
    PickParamsComponent,
    DagDemoComponent,
    GroupByChartsComponent,
    GraphComponent,
    NaiveGroupByChartComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    BrowserAnimationsModule,
    // material components
    MatButtonModule,
    MatCheckboxModule,
    MatToolbarModule,
    MatGridListModule,
    MatTabsModule,
    MatCardModule,
    MatListModule,
    MatSlideToggleModule,
    MatSidenavModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatProgressBarModule,
    MatFormFieldModule,
    MatAutocompleteModule,
    // ngx charts
    NgxChartsModule,
    BarChartModule,
    // ngx dag
    NgxGraphModule,
    // csv parser
    PapaParseModule
  ],
  providers: [
    MainService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
