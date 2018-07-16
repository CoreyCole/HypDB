import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

// angular material components
import {
  MatButtonModule,
  MatCheckboxModule,
  MatToolbarModule,
  MatGridListModule,
  MatTabsModule,
  MatCardModule,
  MatListModule,
  MatSlideToggleModule,
  MatSidenavModule,
  MatInputModule,
  MatSelectModule,
  MatChipsModule
} from '@angular/material';
import 'hammerjs';

// ngx charts
import { BarChartModule } from '@swimlane/ngx-charts';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomePageComponent } from './pages/home-page/home-page.component';
import { MainService } from './services/main.service';
import { BarChartDemoComponent } from './components/bar-chart-demo/bar-chart-demo.component';


@NgModule({
  declarations: [
    AppComponent,
    HomePageComponent,
    BarChartDemoComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule,
    // material components
    MatButtonModule,
    MatCheckboxModule,
    MatToolbarModule,
    MatGridListModule,
    MatTabsModule,
    MatCardModule,
    MatListModule,
    MatSlideToggleModule,
    MatSidenavModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    // ngx charts
    BarChartModule
  ],
  providers: [
    MainService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
