import React, {Component} from "react";
import { Router, Scene } from 'react-native-router-flux';
import MedTrialSearchBar from './MedTrialSearchBar'
import MedTrialSearchResults from './MedTrialSearchResults'
import TrialView from "./TrialView";

export default class MedTrialSearch extends Component {
  render() {
    return (
      <Router hideNavBar= "true">
        <Scene key="root">
          <Scene key="MedTrialSearchBar" component={MedTrialSearchBar} title="Search Clinical Trials" initial={true} />
          <Scene key="MedTrialSearchResults" component={MedTrialSearchResults} title="Search Results" />
          <Scene key="TrialView" component={TrialView} title="Trial Information" />
        </Scene>
      </Router>
    )
  }
}
