#version 420 core
precision mediump float;
layout(binding = 0) uniform sampler2D tex;

in vec2 v_texcoord;
in vec2 v_texcoordOffset[16];

out vec4 FragColor;

vec4 gauss() {
	vec4 sum = vec4(0.0);
	//9x9 或者使用weights(0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216)
	sum += texture(tex, v_texcoord) * 0.18 * 0.5;
	sum += texture(tex, v_texcoordOffset[0]) * 0.05 * 0.5;
	sum += texture(tex, v_texcoordOffset[1]) * 0.09 * 0.5;
	sum += texture(tex, v_texcoordOffset[2]) * 0.12 * 0.5;
	sum += texture(tex, v_texcoordOffset[3]) * 0.15 * 0.5;
	sum += texture(tex, v_texcoordOffset[4]) * 0.15 * 0.5;
	sum += texture(tex, v_texcoordOffset[5]) * 0.12 * 0.5;
	sum += texture(tex, v_texcoordOffset[6]) * 0.09 * 0.5;
	sum += texture(tex, v_texcoordOffset[7]) * 0.05 * 0.5;

	sum += texture(tex, v_texcoordOffset[8]) * 0.05 * 0.5;
	sum += texture(tex, v_texcoordOffset[9]) * 0.09 * 0.5;
	sum += texture(tex, v_texcoordOffset[10]) * 0.12 * 0.5;
	sum += texture(tex, v_texcoordOffset[11]) * 0.15 * 0.5;
	sum += texture(tex, v_texcoordOffset[12]) * 0.15 * 0.5;
	sum += texture(tex, v_texcoordOffset[13]) * 0.12 * 0.5;
	sum += texture(tex, v_texcoordOffset[14]) * 0.09 * 0.5;
	sum += texture(tex, v_texcoordOffset[15]) * 0.05 * 0.5;
	return sum;
}

void main()
{
    vec4 resultColor = gauss();
    FragColor = resultColor;
    // FragColor = vec4(1.0, 1.0, 1.0, 1.0);
}
