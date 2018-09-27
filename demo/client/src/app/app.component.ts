import { Component } from '@angular/core';

@Component({
  selector: 'hyp-root',
  template: `
    <router-outlet></router-outlet>
  `,
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'hyp';
}
