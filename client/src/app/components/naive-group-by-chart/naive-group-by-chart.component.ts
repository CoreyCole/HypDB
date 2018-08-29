import { Component, Input, OnChanges } from '@angular/core';
import { GraphData } from '../../services/main.service';

@Component({
  selector: 'hyp-naive-group-by-chart',
  template: `
  <mat-card>
    <div class="chart">
      <h2>{{ title }}</h2>
      <h3>CMI: {{ cmi }}</h3>
      <h3>95% confidence interval for p-value: ({{ low }}, {{ high }})</h3>
      <ngx-charts-bar-vertical
        [view]="view"
        [scheme]="colorScheme"
        [results]="data"
        [xAxis]="true"
        [yAxis]="true"
        [legend]="false"
        [showXAxisLabel]="true"
        [showYAxisLabel]="true"
        xAxisLabel="{{ treatment }}"
        yAxisLabel="{{ outcome }}">
      </ngx-charts-bar-vertical>
    </div>
  </mat-card>
  `,
  styleUrls: ['./naive-group-by-chart.component.scss']
})
export class NaiveGroupByChartComponent implements OnChanges {
  @Input() data: any[];
  @Input() graphData: GraphData;
  @Input() title: string;
  @Input() cmi: string;
  @Input() low: string;
  @Input() high: string;
  public view: any[] = [400, 400];
  public colorScheme = {
    domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA']
  };
  public treatment: string;
  public outcome: string;

  constructor() { }

  ngOnChanges() {
    console.log(this.data);
    this.treatment = this.graphData.correlation.treatment[0];
    this.outcome = this.graphData.correlation.outcome[0];
  }

}
