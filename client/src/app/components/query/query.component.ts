import { Component, OnInit, Input } from '@angular/core';
import { CsvJson, MainService } from '../../services/main.service';
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
  <hyp-pick-params [csvJson]="csvJson | async"></hyp-pick-params>
  `,
  styleUrls: ['./query.component.scss']
})
export class QueryComponent implements OnInit {
  @Input() files: string[];
  csvJson: Observable<CsvJson>;

  constructor(private main: MainService) { }

  ngOnInit() {
  }

  getCsvJson(filename: string) {
    this.csvJson = this.main.downloadCsvJson(filename);
  }

}
