#version 420 core
precision mediump float;
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTex;

out vec2 v_texcoord;
out vec2 v_texcoordOffset[16];

void main()
{
    float x_singleStepOffset = 3.0/1920.0;
    float y_singleStepOffset = 3.0/1080.0;
    v_texcoordOffset[0] = aTex + vec2(-4.0 * x_singleStepOffset, 0.0);
    v_texcoordOffset[1] = aTex + vec2(-3.0 * x_singleStepOffset, 0.0);
    v_texcoordOffset[2] = aTex + vec2(-2.0 * x_singleStepOffset, 0.0);
    v_texcoordOffset[3] = aTex + vec2(-1.0 * x_singleStepOffset, 0.0);
    v_texcoordOffset[4] = aTex + vec2(1.0 * x_singleStepOffset, 0.0);
    v_texcoordOffset[5] = aTex + vec2(2.0 * x_singleStepOffset, 0.0);
    v_texcoordOffset[6] = aTex + vec2(3.0 * x_singleStepOffset, 0.0);
    v_texcoordOffset[7] = aTex + vec2(4.0 * x_singleStepOffset, 0.0);

    v_texcoordOffset[8] = aTex + vec2(0.0,-4.0 * y_singleStepOffset);
    v_texcoordOffset[9] = aTex + vec2(0.0,-3.0 * y_singleStepOffset);
    v_texcoordOffset[10] = aTex + vec2(0.0,-2.0 * y_singleStepOffset);
    v_texcoordOffset[11] = aTex + vec2(0.0,-1.0 * y_singleStepOffset);
    v_texcoordOffset[12] = aTex + vec2(0.0,1.0 * y_singleStepOffset);
    v_texcoordOffset[13] = aTex + vec2(0.0,2.0 * y_singleStepOffset);
    v_texcoordOffset[14] = aTex + vec2(0.0,3.0 * y_singleStepOffset);
    v_texcoordOffset[15] = aTex + vec2(0.0,4.0 * y_singleStepOffset);

    gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0f);
    v_texcoord = aTex;
}
