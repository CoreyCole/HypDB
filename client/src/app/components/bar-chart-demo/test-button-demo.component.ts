import { Component, OnInit } from '@angular/core';
import { MainService } from '../../services/main.service';
import { of } from 'rxjs'
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'test-button-demo',
  template: `
    <input type="button" value="Submit" (click)="sendJSON()"/>
  `,
  styleUrls: ['./test-button-demo.component.scss'],
})
export class TestButtonDemoComponent implements OnInit {
  constructor(
    private main: MainService
  ) { }

  ngOnInit() {
  }

  sendJSON() {
    this.main.postJSON({hello: "world"})
      .pipe(
        catchError((err: any) => {
          console.error(err);
          return of(err);
        })
      )
      .subscribe(res => console.log(res));
  }

}
