import React, { Component } from "react";
import { Container, Body, Content, Text, Card, CardItem } from "native-base";
import Highlighter from 'react-native-highlight-words';

export default class TrialView extends Component {

  render() {
    trial_data = this.props.trial;
    return (
      <Container>
        <Content>
          <Card>
            <CardItem header>
              <Text>{trial_data.brief_title}</Text>
            </CardItem>
            <CardItem>
              <Body>
                <Text style={{ fontWeight: 'bold' }}>NCT ID : </Text><Text>{trial_data.nct_id}</Text>
                <Text style={{ fontWeight: 'bold' }}>Description : </Text><Highlighter
                  highlightStyle={{ backgroundColor: 'yellow' }}
                  searchWords={this.props.searchInput.trim().split(" ")}
                  textToHighlight={trial_data.detailed_description}
              />
              </Body>
            </CardItem>
            <CardItem footer>
              <Text>{trial_data.url}</Text>
            </CardItem>
          </Card>
        </Content>
      </Container>
    );
  }

}