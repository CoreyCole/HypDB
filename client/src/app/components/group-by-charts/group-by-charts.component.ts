import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'hyp-group-by-charts',
  template: `
  <mat-card>
    <ngx-charts-bar-vertical
      [view]="view"
      [scheme]="colorScheme"
      [results]="ate1"
      [xAxis]="true"
      [yAxis]="true"
      [legend]="true"
      [showXAxisLabel]="true"
      [showYAxisLabel]="true"
      xAxisLabel="Treatment"
      yAxisLabel="Outcome">
    </ngx-charts-bar-vertical>
  </mat-card>
  <mat-card *ngIf="ate2">
    <ngx-charts-bar-vertical-2d
      [view]="view"
      [scheme]="colorScheme"
      [results]="ate2"
      [xAxis]="true"
      [yAxis]="true"
      [legend]="true"
      [showXAxisLabel]="true"
      [showYAxisLabel]="true"
      xAxisLabel="Treatment & Grouping Attribute"
      yAxisLabel="Outcome">
    </ngx-charts-bar-vertical-2d>
  </mat-card>
  `,
  styleUrls: ['./group-by-charts.component.scss']
})
export class GroupByChartsComponent implements OnInit {
  @Input() data: any[];
  public view: any[] = [900, 400];
  public colorScheme = {
    domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA']
  };
  public ate1: any[];
  public ate2: any[];

  constructor() { }

  ngOnInit() {
    this.ate1 = this.data[0];
    if (this.data[1]) {
      this.ate2 = this.data[1];
    }
  }

}
