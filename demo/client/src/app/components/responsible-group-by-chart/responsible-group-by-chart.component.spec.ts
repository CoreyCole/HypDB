import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ResponsibleGroupByChartComponent } from './responsible-group-by-chart.component';

describe('ResponsibleGroupByChartComponent', () => {
  let component: ResponsibleGroupByChartComponent;
  let fixture: ComponentFixture<ResponsibleGroupByChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ResponsibleGroupByChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ResponsibleGroupByChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
