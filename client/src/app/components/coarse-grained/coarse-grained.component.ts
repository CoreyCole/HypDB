import { Component, OnChanges, Input } from '@angular/core';

@Component({
  selector: 'hyp-coarse-grained',
  template: `
  <div class="datatable">
    <mat-toolbar color="accent">
      <span>Coarse Grained Explanations</span>
    </mat-toolbar>
    <ngx-datatable
      class="material"
      [rows]="rows"
      [columns]="columns"
      [columnMode]="'force'"
      [headerHeight]="50"
      [footerHeight]="50"
      [rowHeight]="'auto'">
    </ngx-datatable>
  </div>
  `,
  styleUrls: ['./coarse-grained.component.scss']
})
export class CoarseGrainedComponent implements OnChanges {
  @Input() responsibility: { string: number };
  columns: any[] = [
    { name: 'attribute' },
    { name: 'responsibility' }
  ];
  rows: any[];

  constructor() { }

  ngOnChanges() {
    if (this.responsibility) {
      const attributes = Object.keys(this.responsibility);
      this.rows = attributes.map(attribute => {
        return { attribute, responsibility: this.responsibility[attribute] }
      });
    }
  }

}
