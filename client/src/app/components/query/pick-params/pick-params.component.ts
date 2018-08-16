import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import * as SqlWhereParser from 'sql-where-parser';

import { CsvJson, HypDBDto, QueryRes, MainService } from '../../../services/main.service';

@Component({
  selector: 'hyp-pick-params',
  template: `
  <div *ngIf="csvJson">
    <h1>Query Input</h1>
    <span class="error">{{ error }}</span>
    <div class="inputs">
      <div class="input outcome">
        <h2>Select Outcome of Interest</h2>
        <mat-form-field>
          <mat-select placeholder="column">
            <mat-option *ngFor="let column of csvJson.meta.fields" [value]="column" (click)="selectOutcome(column)">
              {{ column }}
            </mat-option>
          </mat-select>
        </mat-form-field>
      </div>
      <div class="input">
        <h2>Select Subset of Data</h2>
        <mat-form-field class="where">
          <input matInput type="text" placeholder="Subset of data" [(ngModel)]="where" autocomplete="off">
        </mat-form-field>
      </div>
      <div class="input">
        <h2>Select Grouping Attributes</h2>
        <mat-form-field>
          <mat-select placeholder="column">
            <mat-option *ngFor="let column of csvJson.meta.fields" [value]="column" (click)="selectGroupingAttribute(column)">
              {{ column }}
            </mat-option>
          </mat-select>
        </mat-form-field>
      </div>
    </div>
    <pre>SELECT avg({{ outcome }}) </pre>
    <pre>FROM {{ csvJson.meta.filename }}</pre>
    <pre>WHERE {{ where }}</pre>
    <pre>GROUP BY <span *ngFor="let attribute of groupingAttributes">{{ attribute }} </span></pre>
    <div class="spacer"></div>
    <div *ngIf="!loading">
      <button mat-raised-button (click)="clear()">CLEAR</button>
      <button mat-raised-button color="accent" (click)="query()">QUERY</button>
    </div>
    <mat-spinner *ngIf="loading" color="accent"></mat-spinner>
  </div>
  `,
  styleUrls: ['./pick-params.component.scss']
})
export class PickParamsComponent implements OnInit {
  @Input() csvJson: CsvJson;
  @Output() results = new EventEmitter<QueryRes>();
  outcome: string = null;
  groupingAttributes: string[] = [];
  where: string;
  error: string;
  whereParser = new SqlWhereParser();
  loading = false;

  constructor(private main: MainService) { }

  ngOnInit() {
  }

  clear() {
    this.outcome = null;
    this.groupingAttributes = [];
    this.where = '';
  }

  selectOutcome(column: string) {
    this.outcome = column;
  }

  selectGroupingAttribute(column: string) {
    this.groupingAttributes.push(column);
  }

  query() {
    if (!this.outcome) {
      this.error = 'no outcomes selected!';
    } else if (!this.groupingAttributes || this.groupingAttributes.length === 0) {
      this.error = 'no grouping attributes selected!';
    } else {
      this.error = null;
      this.loading = true;
      const parsedWhere = this.whereParser.parse(this.where);
      const dto: HypDBDto = {
        outcome: this.outcome,
        groupingAttributes: this.groupingAttributes,
        filename: this.csvJson.meta.filename,
        where: parsedWhere
      };
      this.main.queryHypDb(dto)
        .subscribe(data => {
          console.log(data);
          this.results.emit(data);
          this.loading = false;
        });
    }
  }

}
