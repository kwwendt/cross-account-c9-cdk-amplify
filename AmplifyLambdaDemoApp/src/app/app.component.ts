import { Component, Input } from '@angular/core';
import { Amplify, API, Auth } from 'aws-amplify';

import awsmobile from '../aws-exports';

Amplify.configure({
  API: {
    endpoints: [
      {
        name: awsmobile['aws_cloud_logic_custom'][0]['name'],
        endpoint: awsmobile['aws_cloud_logic_custom'][0]['endpoint']
      }  
    ]
  }
});

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'AmplifyLambdaDemoApp';
  echoText: string = "";
  responseText: string = "";
  
  constructor() {}
  
  async echo(echoText: string) {
    this.echoText = echoText;
    const apiName = awsmobile['aws_cloud_logic_custom'][0]['name'];
    const path = '/echo';
    const myInit = {
      body: {"Message": `${echoText}`},
      headers: {
        Authorization: `Bearer ${(await Auth.currentSession())
          .getIdToken()
          .getJwtToken()}`
      }
    };
    API.post(apiName, path, myInit)
    .then((response) => {
      this.responseText = response['Message'];
    })
    .catch((error) => {
      console.log(error);
    })
  }
  
  clear() {
    this.echoText = "";
    this.responseText = "";
  }
}
