import { Component, OnChanges, Input } from '@angular/core';

@Component({
  selector: 'hyp-fine-grained',
  template: `
  <div class="datatable">
    <mat-toolbar color="accent">
      <span>Fine Grained Attribute Data</span>
      <span class="flex-span"></span>
      <span class="select-span">
        <mat-select
          #selectedAttribute
          placeholder="attribute"
          [value]="currentCovariate"
          (valueChange)="attributeSelected(selectedAttribute.value)">
          <mat-option *ngFor="let attribute of covariates" [value]="attribute">
            {{ attribute }}
          </mat-option>
        </mat-select>
      </span>
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
  styleUrls: ['./fine-grained.component.scss']
})
export class FineGrainedComponent implements OnChanges {
  @Input() fineGrained: {
    attributes: { string: { columns: string[], rows: any[] } },
    outcome: string[];
    treatment: string[];
  };
  covariates: string[];
  currentCovariate: string;
  columns: any[];
  rows: any[];

  constructor() { }

  ngOnChanges() {
    if (this.fineGrained) {
      this.covariates = Object.keys(this.fineGrained.attributes);
      this.currentCovariate = this.covariates[0];
      this.columns = this.fineGrained.attributes[this.currentCovariate].columns.map(column => {
        return { name: column };
      });
      this.rows = this.fineGrained.attributes[this.currentCovariate].rows;
    }
  }

  attributeSelected(attribute: string) {
    this.currentCovariate = attribute;
    this.columns = this.fineGrained.attributes[attribute].columns.map(column => {
      return { name: column };
    });
    this.rows = this.fineGrained.attributes[attribute].rows;
  }

}
