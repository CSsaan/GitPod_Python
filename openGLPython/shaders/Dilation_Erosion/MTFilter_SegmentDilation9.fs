#version 420 core
precision mediump float;

layout(binding = 0) uniform sampler2D tex;

in vec2 v_texcoord;
in vec2 v_texcoordOffset[16];

out vec4 FragColor;

void main()
{
	vec3 res;
	vec3 tempMax = vec3(0.0);
	
	tempMax = max(texture(tex, v_texcoord).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[3]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[4]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[2]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[5]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[1]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[6]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[0]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[7]).rgb, tempMax);

	tempMax = max(texture(tex, v_texcoordOffset[8]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[9]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[10]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[11]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[12]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[13]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[14]).rgb, tempMax);
	tempMax = max(texture(tex, v_texcoordOffset[15]).rgb, tempMax);
	
	FragColor = vec4(tempMax, 1.0);
}


