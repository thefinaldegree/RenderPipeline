#version 430


#pragma include "../../Native/Source/common.h"

layout(local_size_x=256, local_size_y=1, local_size_z=1) in;

// This shader takes the list of rendered objects with their transforms, 
// and spawns a strip for each rendered object

// uniform samplerBuffer DrawnObjectsTex;
uniform sampler2D DrawnObjectsTex;


uniform isampler2D MappingTex;
uniform layout(r32i) iimageBuffer IndirectTex;
uniform writeonly iimageBuffer DynamicStripsTex;
uniform sampler2D DatasetTex;


uniform vec3 cameraPosition;


const float HALF_PI = 1.57079632679;
const float TWO_PI = 6.28318530718;



void main() {

    int thread_id = int(gl_GlobalInvocationID.x);

    // int num_objects_drawn = int(texelFetch(DrawnObjectsTex, 0).x + 0.5);
    int num_objects_drawn = int(texelFetch(DrawnObjectsTex, ivec2(0), 0 ).b + 0.5);

    // Reset counter in the beginning

    if (thread_id == 0) {
        imageStore(IndirectTex, 0, ivec4(SG_TRI_GROUP_SIZE * 3));
        imageStore(IndirectTex, 1, ivec4(0));
        imageStore(IndirectTex, 2, ivec4(0));
        imageStore(IndirectTex, 3, ivec4(0));
    }

    barrier();

    // For each drawn object
    if (thread_id < num_objects_drawn) {

        // Fetch the id of the object
        int read_offs = 1 + thread_id * 5;
        // int object_id = int(texelFetch(DrawnObjectsTex, read_offs).x + 0.5);
        int object_id = int(texelFetch(DrawnObjectsTex, ivec2(read_offs, 0), 0 ).b + 0.5);

        // Extract projection mat
        // vec4 mt0 = texelFetch(DrawnObjectsTex, read_offs + 1).rgba;
        // vec4 mt1 = texelFetch(DrawnObjectsTex, read_offs + 2).rgba;
        // vec4 mt2 = texelFetch(DrawnObjectsTex, read_offs + 3).rgba;
        // vec4 mt3 = texelFetch(DrawnObjectsTex, read_offs + 4).rgba;

        vec4 mt0 = texelFetch(DrawnObjectsTex, ivec2(read_offs + 1, 0), 0).bgra;
        vec4 mt1 = texelFetch(DrawnObjectsTex, ivec2(read_offs + 2, 0), 0).bgra;
        vec4 mt2 = texelFetch(DrawnObjectsTex, ivec2(read_offs + 3, 0), 0).bgra;
        vec4 mt3 = texelFetch(DrawnObjectsTex, ivec2(read_offs + 4, 0), 0).bgra;
    

        mat4 obj_transform = mat4(mt0, mt1, mt2, mt3);

        // Check out how many triangle strips the object has
        int num_strips = texelFetch(MappingTex, ivec2(0, object_id), 0).x;

        for (int k = 0; k < num_strips; ++k) {

            // Find the id of the triangle strip
            // Increase k by 1 since the first entry is the number of strips
            int strip_id = texelFetch(MappingTex, ivec2(k + 1, object_id), 0).x;

            // Find strip bounds
            vec4 strip_data_0 = texelFetch(DatasetTex, ivec2(0, strip_id), 0).bgra;
            vec4 strip_data_1 = texelFetch(DatasetTex, ivec2(1, strip_id), 0).bgra;
            vec4 strip_data_2 = texelFetch(DatasetTex, ivec2(2, strip_id), 0).bgra;

            vec3 strip_bb_min = strip_data_0.xyz;
            vec3 strip_bb_max = strip_data_1.xyz;

            // Get strip position in world space
            vec3 strip_bb_mid = (strip_bb_min + strip_bb_max) * 0.5;
            // strip_bb_mid = vec3(0);
            vec3 strip_mid_world = (obj_transform * vec4(strip_bb_mid, 1)).xyz;
            vec3 vec_to_obj = normalize(cameraPosition - strip_mid_world);
            vec3 common_vec = normalize(strip_data_2.xyz);
            float max_angle = strip_data_2.w;

            float angle_diff = acos((dot(common_vec, vec_to_obj)));

            if (angle_diff > max_angle + HALF_PI )  {
                continue;
            } 


            int offset = imageAtomicAdd(IndirectTex, 1, 1) + 0;

            imageStore(DynamicStripsTex, offset, ivec4(thread_id, strip_id, 0, 0));
            // imageStore(DynamicStripsTex, offset + 2, ivec4(strip_id));

        }
    }
}