import React, { Component } from "react";
import { Actions } from 'react-native-router-flux';
import { Container, Header, Title, Left, Icon, Right, Button, Body, Content, Text, Item, Label, Input } from "native-base";

export default class MedTrialSearchBar extends Component {
  render() {
    return (
      <Container>
        <Content padder>
          <Item floatingLabel style={{ marginTop: 20 }}>
            <Label>Keywords</Label>
            <Input />
          </Item>
          <Button full rounded dark
            style={{ marginTop: 10 }}
            onPress={() => Actions.MedTrialSearchResults()}>
            <Left />
            <Text>Search</Text>
            <Right />
          </Button>
        </Content>
      </Container>
    );
  }
}