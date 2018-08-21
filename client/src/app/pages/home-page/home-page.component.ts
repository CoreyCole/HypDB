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
    <hyp-query [files]="main.files | async" (naiveAte)="displayNaiveAte($event)" (results)="displayResults($event)" (clear)="fileChanged()"></hyp-query>
    <span class="error">{{ error }}</span>
    <hyp-naive-group-by-chart *ngIf="!error && naiveAteData" [data]="naiveAteData" [graphData]="naiveGraphData"></hyp-naive-group-by-chart>
    <!-- <hyp-group-by-charts *ngIf="!error && ateData" [data]="ateData" [graphData]="graph"></hyp-group-by-charts> -->
    <span *ngIf="graph" class="error">Bias Detected! Try weighted average query instead...</span>
    <div class="weighted-avg-query">
<pre *ngIf="graph">
SELECT WITH BLOCKS ...
</pre>
    </div>
    <h2 *ngIf="graph">Causal Graph</h2>
    <hyp-graph [graph]="graph"></hyp-graph>
  </div>
  `,
  styleUrls: ['./home-page.component.scss']
})
export class HomePageComponent implements OnInit {
  ateData: any[] = null;
  naiveAteData: any[] = null;
  naiveGraphData: GraphData = null;
  graph: GraphData = null;
  error: string = null;

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
    // this.naiveAteData = this.parseAte(data['naiveAte']);
    // const ate2 = data['ate'][1] ? this.parseAteWithGroupingAttribute(data['ate'][1]) : null;
    this.graph = data['graph'];
  }

  fileChanged() {
    this.naiveAteData = null;
    this.naiveGraphData = null;
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
