import gql from 'graphql-tag'


export const OBJ_DETECT_IMG_QUERY = gql`
query ObjDetectImageQuery($id:String!, $project:String!) {
    objDetectImage(id: $id, project: $project) {
        id
        project
        src
        boundingBoxes {
          	id
            label
            coords {
                x
                y
                width
                height
            }
        }
    }
  }
`;

export const OBJ_DETECT_LABEL_OPT_QUERY = gql`
query ObjDetectLabelOptQuery($project:String!) {
    objDetectLabelOpts(project: $project) {
        labels {
          	value
            color
        }
    }
}
`;