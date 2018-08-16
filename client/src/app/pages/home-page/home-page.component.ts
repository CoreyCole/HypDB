import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';

import { MainService, CsvJson, GraphData, QueryRes } from '../../services/main.service';

@Component({
  selector: 'hyp-home-page',
  template: `
  <div class="container">
    <hyp-csv-upload (uploadedFile)="refreshFiles()"></hyp-csv-upload>
    <hyp-query [files]="files | async" (results)="displayResults($event)" (fileChanged)="fileChanged()"></hyp-query>
    <span class="error">{{ error }}</span>
    <hyp-group-by-charts *ngIf="!error && ateData" [data]="ateData" [graphData]="graph"></hyp-group-by-charts>
    <div class="spacer"></div>
    <hyp-dag-demo></hyp-dag-demo>
  </div>
  `,
  styleUrls: ['./home-page.component.scss']
})
export class HomePageComponent implements OnInit {
  files: Observable<string[]>
  ateData: any[];
  graph: GraphData;
  error: string;

  constructor(
    private main: MainService
  ) { }

  ngOnInit() {
    this.main.test().subscribe(res => console.log(res));
    this.files = this.main.getCsvJsonUploadList();
  }

  refreshFiles() {
    this.files = this.main.getCsvJsonUploadList();
  }

  displayResults(data: QueryRes) {
    if (!data['ate'] || data['ate'].length === 0) {
      return this.error = 'Query error!';
    }
    this.error = null;
    const ate1 = this.parseAte(data['ate'][0]);
    const ate2 = data['ate'][1] ? this.parseAteWithGroupingAttribute(data['ate'][1]) : null;
    this.ateData = [
      ate1, ate2
    ];
    this.graph = data['graph'];
  }

  fileChanged() {
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

  private parseGraph(graphData: GraphData) {

  }

}
