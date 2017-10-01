import gql from 'graphql-tag'


export const SAVE_OBJ_DETECT_IMAGE = gql`
mutation SaveObjDetectImage($id: String!, $project: String!, 
                            $annotations: [AnnotationInput]) {
    saveObjDetectImage(id: $id, project: $project, 
                       annotations: $annotations) {
        id
    }
}
`

export const NEXT_OBJ_DETECT_IMG_QUERY = gql`
query NextObjDetectImage($project:String!) {
    nextObjDetectImage(project: $project) {
        id
        project
        src
        annotations {
            id
            label
            bbox {
                id
                annoId
                label
                score
                xmin
                ymin
                xmax
                ymax
                points {
                    id
                    x
                    y
                }
            }
            polygon {
                id
                annoId
                label
                score
                points {
                    id
                    x
                    y
                }
            }
        }
        labels {
          color
          text
          value
        }
    }
  }
`;

export const OBJ_DETECT_IMG_QUERY = gql`
query ObjDetectImageQuery($id:String!, $project:String!) {
    objDetectImage(id: $id, project: $project) {
        id
        project
        src
        bboxes {
          	id
            label
            score
            xmin
            ymin
            xmax
            ymax
        }
        labels {
            color
            text
            value
        }
    }
  }
`;

export const OBJ_DETECT_LABEL_OPT_QUERY = gql`
query ObjDetectLabelOptQuery($project:String!) {
    objDetectLabelOpts(project: $project) {
        labels {
            value
            text
            color
        }
    }
}
`;