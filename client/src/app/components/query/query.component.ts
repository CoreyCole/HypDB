import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { CsvJson, QueryRes, MainService } from '../../services/main.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'hyp-query',
  template: `
  <h1>Select CSV file</h1>
  <mat-form-field>
    <mat-select placeholder="input file">
      <mat-option *ngFor="let file of files" [value]="file" (blur)="getCsvJson(file)">
        {{ file.substring(0, file.length - 5) }}
      </mat-option>
    </mat-select>
  </mat-form-field>
  <hyp-pick-params [csvJson]="csvJson | async" (results)="queryResults($event)"></hyp-pick-params>
  `,
  styleUrls: ['./query.component.scss']
})
export class QueryComponent implements OnInit {
  @Input() files: string[];
  @Output() results = new EventEmitter<QueryRes>();
  csvJson: Observable<CsvJson>;

  constructor(private main: MainService) { }

  ngOnInit() {
  }

  getCsvJson(filename: string) {
    this.csvJson = this.main.downloadCsvJson(filename);
  }

  queryResults(data: QueryRes) {
    this.results.emit(data);
  }

}
