import React, { Component } from "react";
import { Actions } from 'react-native-router-flux';
import { Container, Left, Right, Button, Content, Text, Item, Label, Input } from "native-base";

export default class MedTrialSearchBar extends Component {

  constructor(props) {
    super(props);
    this.state = {
      searchInput: ''
    };
  }

  render() {
    return (
      <Container>
        <Content padder>
          <Item floatingLabel style={{ marginTop: 20 }}>
            <Label>Keywords</Label>
            <Input value={this.state.searchInput} editable={true} onChangeText={(text) => this.setState({searchInput:text})}/>
          </Item>
          <Button full rounded dark
            style={{ marginTop: 10 }}
            onPress={() => Actions.MedTrialSearchResults({searchInput: this.state.searchInput})}>
            <Left />
            <Text>Search</Text>
            <Right />
          </Button>
        </Content>
      </Container>
    );
  }
}