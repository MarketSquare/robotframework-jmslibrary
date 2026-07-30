*** Settings ***
Library  JMS    classpath=/temp/*

*** Test Cases ***
Create Connection without jar files
    Run Keyword and expect error    Failed to create connection    Create Connection
