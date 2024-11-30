#iChannel0 "file://D:/OpenGlProject/ShaderToys/pic/depth/1118.png"





void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord / iResolution.xy;


    fragColor = texture(iChannel0, uv);
}