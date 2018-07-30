import { Component, OnInit } from '@angular/core';
import { MainService } from '../../services/main.service';

@Component({
  selector: 'hyp-home-page',
  template: `
    <hyp-bar-chart-demo></hyp-bar-chart-demo>
    <test-button-demo></test-button-demo>
  `,
  styleUrls: ['./home-page.component.scss']
})
export class HomePageComponent implements OnInit {

  constructor(
    private main: MainService
  ) { }

  ngOnInit() {
    this.main.test().subscribe(res => console.log(res));
  }

}
