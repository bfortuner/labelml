#!/bin/sh

echo 'query TodoListQuery { todoList { todos { id text completed } } }' | http post http://localhost:5000/graphql content-type:application/graphql
