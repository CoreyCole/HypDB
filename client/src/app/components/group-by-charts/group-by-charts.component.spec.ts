import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GroupByChartsComponent } from './group-by-charts.component';

describe('GroupByChartsComponent', () => {
  let component: GroupByChartsComponent;
  let fixture: ComponentFixture<GroupByChartsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GroupByChartsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GroupByChartsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
