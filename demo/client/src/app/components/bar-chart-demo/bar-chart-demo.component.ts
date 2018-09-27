import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'hyp-bar-chart-demo',
  template: `
<ngx-charts-bar-vertical-2d
  [view]="view"
  [scheme]="colorScheme"
  [results]="simpsonsParadox.data"
  [xAxis]="true"
  [yAxis]="true"
  [legend]="true"
  [showXAxisLabel]="true"
  [showYAxisLabel]="true"
  [xAxisLabel]="simpsonsParadox.xAxis"
  [yAxisLabel]="simpsonsParadox.yAxis">
</ngx-charts-bar-vertical-2d>
  `,
  styleUrls: ['./bar-chart-demo.component.scss']
})
export class BarChartDemoComponent implements OnInit {
  public view: any[] = [900, 400];
  public colorScheme = {
    domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA']
  };
  public simpsonsParadox = {
    'xAxis': 'Airport',
    'yAxis': 'Average Delayed Flights',
    'data': [
      {
        'name': 'COS',
        'series': [
          {
            'name': 'AA',
            'value': 0.11
          },
          {
            'name': 'UA',
            'value': 0.08
          }
        ]
      },
      {
        'name': 'MFE',
        'series': [
          {
            'name': 'AA',
            'value': 0.09
          },
          {
            'name': 'UA',
            'value': 0.071
          }
        ]
      },
      {
        'name': 'MTJ',
        'series': [
          {
            'name': 'AA',
            'value': 0.17
          },
          {
            'name': 'UA',
            'value': 0.16
          }
        ]
      },
      {
        'name': 'ROC',
        'series': [
          {
            'name': 'AA',
            'value': 0.22
          },
          {
            'name': 'UA',
            'value': 0.21
          }
        ]
      }
    ]
  };

  constructor() { }

  ngOnInit() {
  }

}
