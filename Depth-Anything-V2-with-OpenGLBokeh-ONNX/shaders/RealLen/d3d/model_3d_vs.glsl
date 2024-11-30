attribute vec4 aPosition;
attribute vec2 aTexCoord;

uniform mat4 textureMatrix;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

varying vec2 textureCoordinate;

void main() {
    textureCoordinate = (textureMatrix * vec4(aTexCoord, 0.0, 1.0)).xy;
    vec4 pos = projection * view * model * aPosition;
    gl_Position = pos;
}