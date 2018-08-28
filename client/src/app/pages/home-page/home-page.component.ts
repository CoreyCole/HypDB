import { Component, OnInit } from '@angular/core';
import { Observable, of } from 'rxjs';

import { MainService, CsvJson, GraphData, QueryRes } from '../../services/main.service';

@Component({
  selector: 'hyp-home-page',
  template: `
  <mat-toolbar color="primary">
    HypDB
    <span class="flex-span"></span>
    <button mat-raised-button color="accent" routerLink="/upload">UPLOAD CSV FILE</button>
  </mat-toolbar>
  <div class="container">
    <div class="query-chart-row">
      <mat-card class="query-card main-query">
        <hyp-query [files]="main.files | async" (naiveAte)="displayNaiveAte($event)" (results)="displayResults($event)" (clear)="fileChanged()"></hyp-query>
        <span class="error">{{ error }}</span>
      </mat-card>
      <div class="chart-cards" *ngIf="!error && naiveAteData">
        <hyp-naive-group-by-chart [data]="naiveAteData" [graphData]="naiveGraphData" title="Naive Group By Results"></hyp-naive-group-by-chart>
        <!-- <hyp-group-by-charts *ngIf="!error && ateData" [data]="ateData" [graphData]="graph"></hyp-group-by-charts> -->
      </div>
    </div>
    <div class="query-chart-row" *ngIf="graph">
      <mat-card class="query-card">
        <h1>{{ mostResponsible }} has the highest responsibility for making this query biased</h1>
        <pre *ngFor="let line of queryChartData[1].query" class="sql">{{ line }}</pre>
      </mat-card>
      <div class="chart-cards">
        <hyp-responsible-group-by-chart [data]="queryChartData[1].chart" [graphData]="graph" [mostResponsible]="mostResponsible"></hyp-responsible-group-by-chart>
      </div>
    </div>
    <div class="query-chart-row" *ngIf="graph">
      <mat-card class="query-card">
        <h1>Total Effect Query</h1>
        <pre *ngFor="let line of queryChartData[3].query" class="sql">{{ line }}</pre>
      </mat-card>
      <div class="chart-cards">
        <hyp-naive-group-by-chart [data]="queryChartData[3].chart" [graphData]="graph" title="Total Effect"></hyp-naive-group-by-chart>
      </div>
      <div class="chart-cards">
        <hyp-naive-group-by-chart [data]="queryChartData[2].chart" [graphData]="graph" title="Direct Effect"></hyp-naive-group-by-chart>
      </div>
    </div>
    <div class="datatable-cards" *ngIf="graph">
      <hyp-coarse-grained [responsibility]="responsibility"></hyp-coarse-grained>
      <hyp-fine-grained [fineGrained]="fineGrained"></hyp-fine-grained>
    </div>
    <div class="weighted-avg-query">
    </div>
    <div class="graph" *ngIf="graph">
      <h2>Causal Graph</h2>
      <hyp-graph [graph]="graph"></hyp-graph>
    </div>
  </div>
  `,
  styleUrls: ['./home-page.component.scss']
})
export class HomePageComponent implements OnInit {
  ateData: any[] = null;
  naiveAteData: any[] = null;
  responsibleAteData: any[] = null;
  mostResponsible: string = null;
  fineGrained: any;
  responsibility: { string: number };
  naiveGraphData: GraphData = null;
  rewrittenSql: string[];
  graph: GraphData = null;
  error: string = null;
  queryChartData: { type: string, query: string[], chart: any[] }[];

  constructor(
    public main: MainService
  ) { }

  ngOnInit() {
    this.main.test().subscribe(res => console.log(res));
    this.main.files = this.main.getCsvJsonUploadList();
    window.scrollTo(0, 0);
  }

  displayNaiveAte(data: any[]) {
    console.log('naive data=', data);
    if (!data || data.length === 0) {
      return this.error = 'Naive Query Error!';
    }
    this.error = null;
    this.naiveAteData = this.parseAte(data['naiveAte']);
    this.naiveGraphData = data['graph'];
  }

  displayResults(data: QueryRes) {
    if (!data['naiveAte'] || data['naiveAte'].length === 0) {
      return this.error = 'Query error!';
    }
    this.error = null;
    this.queryChartData = [];
    for (const queryChart of data['data']) {
      if (queryChart.type === 'responsibleAte') {
        queryChart.chart = this.parseAteWithGroupingAttribute(queryChart.chart);
      } else {
        queryChart.chart = queryChart.chart.map(row => {
          const keys = Object.keys(row);
          return { name: row[keys[0]], value: row[keys[1]] };
        });
      }
      this.queryChartData.push(queryChart);
    }
    const covariates = Object.keys(data['responsibility']);
    this.mostResponsible = covariates.reduce((prev, curr) =>
      data['responsibility'][curr] > data['responsibility'][prev] ? curr : prev, covariates[0]);
    this.fineGrained = data['fine_grained'];
    this.responsibility = data['responsibility'];
    this.graph = data['graph'];
  }

  fileChanged() {
    this.naiveAteData = null;
    this.naiveGraphData = null;
    this.responsibleAteData = null;
    this.mostResponsible = null;
    this.responsibility = null
    this.fineGrained = null;
    this.ateData = null;
    this.graph = null;
    this.error = null;
  }

  private parseAte(ateData: any[]) {
    const ate = [];
    const keys = Object.keys(ateData[0]);
    const treatment = keys[0];
    const outcome = keys[1];
    for (const ateRow of ateData) {
      ate.push({
        name: ateRow[treatment],
        value: ateRow[outcome]
      });
    }
    console.log(ate);
    return ate;
  }

  private parseAteWithGroupingAttribute(ateData: any[]) {
    const ate = [];
    const keys = Object.keys(ateData[0]);
    const treatment = keys[0];
    const groupingAttr = keys[1];
    const outcome = keys[2];
    const currentGroup = ateData[0][groupingAttr];
    ate.push({
      name: currentGroup,
      series: []
    });
    for (const ateRow of ateData) {
      const nextGroup = ateRow[groupingAttr];
      if (nextGroup !== currentGroup) {
        ate.push({
          name: nextGroup,
          series: []
        });
      }
      ate[ate.length - 1]['series'].push({
        name: ateRow[treatment],
        value: '' + ateRow[outcome]
      });
    }
    return ate;
  }

}
