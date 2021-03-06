import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { FileCheckerComponent } from './file-checker/file-checker.component';
import { LoginComponent } from './login/login.component';
import { MyAccountComponent } from './my-account/my-account.component';
import { UploadQComponent } from './upload-q/upload-q.component';
import { ContestComponent } from './contest/contest.component';
import { ScoreComponent } from './score/score.component';
import { AdminComponent } from './admin/admin.component';
import { BoardEditComponent } from './board-edit/board-edit.component';

const routes: Routes = [
  { path: 'file-checker', component: FileCheckerComponent },
  { path: 'login', component: LoginComponent },
  { path: 'my-account', component: MyAccountComponent },
  { path: 'upload-q', component: UploadQComponent },
  { path: 'arena', component: ContestComponent },
  { path: 'score', component: ScoreComponent },
  { path: 'admin', component: AdminComponent },
  { path: 'edit', component: BoardEditComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {useHash: true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
