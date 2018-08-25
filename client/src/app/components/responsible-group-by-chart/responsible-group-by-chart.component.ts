import { Component, OnChanges, Input } from '@angular/core';
import { GraphData } from '../../services/main.service';

@Component({
  selector: 'hyp-responsible-group-by-chart',
  template: `
  <mat-card>
    <div class="chart" *ngIf="data && data.length > 0">
      <h2>Further grouping by {{ treatment }} and {{ mostResponsible }}</h2>
      <ngx-charts-bar-vertical-2d
        [view]="view"
        [scheme]="colorScheme"
        [results]="data"
        [xAxis]="true"
        [yAxis]="true"
        [legend]="true"
        [showXAxisLabel]="true"
        [showYAxisLabel]="true"
        xAxisLabel="{{ treatment }} Further grouped by {{ mostResponsible }}"
        yAxisLabel="{{ outcome }}">
      </ngx-charts-bar-vertical-2d>
    </div>
  </mat-card>
  `,
  styleUrls: ['./responsible-group-by-chart.component.scss']
})
export class ResponsibleGroupByChartComponent implements OnChanges {
  @Input() data: any[];
  @Input() graphData: GraphData;
  @Input() mostResponsible: string;
  public view: any[] = [1000, 400];
  public colorScheme = {
    domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA']
  };
  treatment: string = null;
  outcome: string = null;

  constructor() { }

  ngOnChanges() {
    this.treatment = this.graphData.correlation.treatment[0];
    this.outcome = this.graphData.correlation.outcome[0];
  }

}
