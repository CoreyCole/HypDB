import { Component, OnInit } from '@angular/core';
import { Observable, of } from 'rxjs';

import { MainService, CsvJson, GraphData, QueryRes } from '../../services/main.service';

@Component({
  selector: 'hyp-home-page',
  template: `
  <mat-toolbar class="main-toolbar" color="primary">
    <img src="/assets/scale.png" alt="hypdb logo">
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
      <span class="flex-span"></span>
      <div class="chart-cards" *ngIf="!error && naiveAteData">
        <hyp-naive-group-by-chart [data]="naiveAteData" [cmi]="naiveCmi" [low]="naiveLow" [high]="naiveHigh" [graphData]="naiveGraphData" title="Naive Group By Results"></hyp-naive-group-by-chart>
        <!-- <hyp-group-by-charts *ngIf="!error && ateData" [data]="ateData" [graphData]="graph"></hyp-group-by-charts> -->
      </div>
      <span class="flex-span"></span>
    </div>
    <div class="query-chart-row" *ngIf="graph">
      <mat-card class="query-card">
        <h1>Further grouping by {{ mostResponsible }} may lead to a different insight...</h1>
        <span class="spacer"></span>
        <pre *ngFor="let line of queryChartData[1].query" class="sql further-query">{{ line }}</pre>
      </mat-card>
      <span class="flex-span"></span>
      <div class="chart-cards">
        <hyp-responsible-group-by-chart [data]="queryChartData[1].chart" [cmi]="queryChartData[1]['cmi']" [low]="queryChartData[1]['low']" [high]="queryChartData[1]['high']" [graphData]="graph" [mostResponsible]="mostResponsible"></hyp-responsible-group-by-chart>
      </div>
      <span class="flex-span"></span>
    </div>
    <div class="query-chart-row" *ngIf="graph">
      <mat-card class="query-card" *ngIf="queryChartData[3].chart && queryChartData[3].chart.length > 0">
        <h1>Total Effect Query</h1>
        <pre *ngFor="let line of queryChartData[3].query" class="sql">{{ line }}</pre>
      </mat-card>
      <div class="tede">
        <div class="tede-chart-cards">
          <span class="flex-span" *ngIf="queryChartData[3].chart && queryChartData[3].chart.length > 0"></span>
          <hyp-naive-group-by-chart *ngIf="queryChartData[3].chart && queryChartData[3].chart.length > 0" 
            [data]="queryChartData[3].chart" 
            [cmi]="queryChartData[3]['cmi']" 
            [low]="queryChartData[3]['low']" 
            [high]="queryChartData[3]['high']" 
            [graphData]="graph" 
            title="Total Effect">
          </hyp-naive-group-by-chart>
          <span class="flex-span"></span>
          <hyp-naive-group-by-chart *ngIf="queryChartData[2].chart && queryChartData[2].chart.length > 0" 
            [data]="queryChartData[2].chart" 
            [cmi]="queryChartData[2]['cmi']" 
            [low]="queryChartData[2]['low']" 
            [high]="queryChartData[2]['high']" 
            [graphData]="graph" 
            title="Direct Effect">
          </hyp-naive-group-by-chart>
          <span class="flex-span" *ngIf="queryChartData[2].chart && queryChartData[2].chart.length > 0"></span>
        </div>
        <div class="cov-container">
          <span class="flex-span"></span>
          <mat-card class="covariates">
            <h3>Covariates</h3>
            <span *ngFor="let cov of covariates; index as i">{{ cov }}{{ (i < covariates.length - 1) ? ', ' : ''}}</span>
            <h3>Mediator</h3>
            <span *ngFor="let cov of mediator; index as i">{{ cov }}{{ (i < mediator.length - 1) ? ', ' : ''}}</span>
          </mat-card>
          <span class="flex-span"></span>
        </div>
      </div>
    </div>
    <div class="datatable-cards" *ngIf="graph">
      <span class="flex-span"></span>
      <hyp-coarse-grained [responsibility]="responsibility"></hyp-coarse-grained>
      <hyp-fine-grained [fineGrained]="fineGrained"></hyp-fine-grained>
      <span class="flex-span"></span>
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
  covariates: string[];
  mediator: string[];
  naiveLow: string;
  naiveHigh: string;
  naiveCmi: string;

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
    this.naiveLow = data['low'];
    this.naiveHigh = data['high'];
    this.naiveCmi = data['cmi'];
    // this.naiveAteData = [
    //   { name: "AA", value: 0.0598 },
    //   { name: "UA", value: 0.0644 }
    // ]
    this.naiveGraphData = data['graph'];
  }

  displayResults(data: QueryRes) {
    if (!data['naiveAte'] || data['naiveAte'].length === 0) {
      return this.error = 'Query error!';
    }
    this.error = null;
    this.queryChartData = [];
    for (const queryChart of data['data']) {
      if (queryChart.chart && queryChart.chart.length > 0) {
        if (queryChart.type === 'responsibleAte') {
          queryChart.chart = this.parseAteWithGroupingAttribute(queryChart.chart);
        } else {
          queryChart.chart = queryChart.chart.map(row => {
            const keys = Object.keys(row);
            return { name: row[keys[0]], value: row[keys[1]] };
          });
        }
        this.queryChartData.push(queryChart);
      } else {
        this.queryChartData.push({ type: '', chart: [], query: [] });
      }
    }
    this.covariates = data['covariates'];
    this.mediator = data['mediator'];
    const resKeys = Object.keys(data['responsibility']);
    this.mostResponsible = resKeys.reduce((prev, curr) =>
      data['responsibility'][curr] > data['responsibility'][prev] ? curr : prev, resKeys[0]);
    const keys = Object.keys(data['fine_grained'].attributes);
    for (const key of keys) {
      data['fine_grained'].attributes[key].columns.unshift('k');
      data['fine_grained'].attributes[key].rows = data['fine_grained'].attributes[key].rows.map((row, index) => {
        return { k: index + 1, ...row };
      });
    }
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
