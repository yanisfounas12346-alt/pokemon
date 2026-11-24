#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: smoke ROM output-prefix < input (frames mask)\n"); return 2; }
    struct mCore *core = mCoreCreate(mPLATFORM_GBA);
    if (!core || !core->init(core)) return 3;
    mCoreInitConfig(core, "smoke");
    struct VFile *rom = VFileOpen(argv[1], O_RDONLY);
    if (!rom || !core->loadROM(core, rom)) return 4;
    unsigned w,h; core->desiredVideoDimensions(core,&w,&h);
    color_t *pixels = calloc(w*h,sizeof(color_t)); if (!pixels) return 5;
    core->setVideoBuffer(core,pixels,w);
    core->reset(core);
    char audioName[1024]; snprintf(audioName,sizeof(audioName),"%s-audio.pcm",argv[2]);
    FILE *audio = fopen(audioName,"wb"); if(!audio) return 8;
    core->setAudioBufferSize(core,2048);
    blip_t *left=core->getAudioChannel(core,0), *right=core->getAudioChannel(core,1);
    blip_set_rates(left,core->frequency(core),32768);
    blip_set_rates(right,core->frequency(core),32768);
    unsigned frames, mask, total=0, step=0;
    while (scanf("%u %u",&frames,&mask)==2) {
        if (frames>10000 || total+frames>200000 || mask>1023) return 6;
        core->setKeys(core,mask);
        for(unsigned i=0;i<frames;i++) {
            core->runFrame(core);
            int n=blip_samples_avail(left);
            if(n>blip_samples_avail(right)) n=blip_samples_avail(right);
            while(n>0) {
                short stereo[4096]; int k=n>2048?2048:n;
                blip_read_samples(left,stereo,k,1);
                blip_read_samples(right,stereo+1,k,1);
                fwrite(stereo,sizeof(short),k*2,audio); n-=k;
            }
        }
        total+=frames;
        char name[1024]; snprintf(name,sizeof(name),"%s-%03u.ppm",argv[2],step++);
        FILE *f=fopen(name,"wb"); if(!f)return 7;
        fprintf(f,"P6\n%u %u\n255\n",w,h);
        for(unsigned i=0;i<w*h;i++){ uint32_t p=pixels[i]; unsigned char rgb[3]={p&255,(p>>8)&255,(p>>16)&255}; fwrite(rgb,1,3,f); }
        fclose(f); printf("frames=%u core=%u\n",total,core->frameCounter(core)); fflush(stdout);
    }
    fclose(audio); core->deinit(core); free(pixels); return 0;
}
