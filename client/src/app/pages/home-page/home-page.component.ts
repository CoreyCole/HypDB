import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';

import { MainService, CsvJson } from '../../services/main.service';

@Component({
  selector: 'hyp-home-page',
  template: `
    <div class="container">
      <hyp-csv-upload></hyp-csv-upload>
      <hyp-query [files]="files | async"></hyp-query>
      <hyp-bar-chart-demo></hyp-bar-chart-demo>
    </div>
  `,
  styleUrls: ['./home-page.component.scss']
})
export class HomePageComponent implements OnInit {
  files: Observable<string[]>

  constructor(
    private main: MainService
  ) { }

  ngOnInit() {
    this.main.test().subscribe(res => console.log(res));
    this.files = this.main.getCsvJsonUploadList();
  }

}
