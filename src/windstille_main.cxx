//  $Id: windstille_main.cxx,v 1.28 2003/11/07 13:00:39 grumbel Exp $
//
//  Windstille - A Jump'n Shoot Game
//  Copyright (C) 2000 Ingo Ruhnke <grumbel@gmx.de>
//
//  This program is free software; you can redistribute it and/or
//  modify it under the terms of the GNU General Public License
//  as published by the Free Software Foundation; either version 2
//  of the License, or (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

#include <config.h>
//#include <ClanLib/gl.h>
#include <ClanLib/core.h>
#include <ClanLib/vorbis.h>
#include <ClanLib/sound.h>
#include <ClanLib/display.h>

#include <guile/gh.h>

#include "string_converter.hxx"
#include "windstille_error.hxx"
#include "globals.hxx"
#include "editor/editor.hxx"
#include "windstille_game.hxx"
#include "guile_gameobj_factory.hxx"
#include "windstille_level.hxx"
#include "windstille_main.hxx"
#include "windstille_menu.hxx"
#include "keyboard_controller.hxx"
#include "gamepad_controller.hxx"
#include "fonts.hxx"
#include "music_manager.hxx"
#include "tile_factory.hxx"

extern "C" void SWIG_init(void);

CL_ResourceManager* resources;

WindstilleMain::WindstilleMain()
{
  screen_width  = 800;
  screen_height = 600;
  fullscreen    = false;
  allow_resize  = false;
  joystick_id   = -1;
  launch_editor = false;
}

WindstilleMain::~WindstilleMain()
{
}

void
WindstilleMain::parse_command_line(int argc, char** argv)
{
  CL_CommandLine argp;
    
  argp.set_help_indent(22);
  argp.add_usage ("[LEVELFILE]");
  argp.add_doc   ("Windstille is a classic Jump'n Run game.");

  argp.add_group("Display Options:");
  argp.add_option('g', "geometry",   "WxH", "Change window size to WIDTH and HEIGHT");
  argp.add_option('f', "fullscreen", "", "Launch the game in fullscreen");

  argp.add_group("Controlls Options:");
  argp.add_option('j', "joystick", "NUM", "Use joystick number NUM instead of keyboard");

  argp.add_group("Misc Options:");
  argp.add_option('e', "editor",     "", "Launch the level editor");
  argp.add_option('d', "debug",      "", "Turn on debug output");
  argp.add_option('h', "help",       "", "Print this help");

  argp.parse_args(argc, argv);

  while (argp.next())
    {
      switch (argp.get_key())
        {
        case 'd':
          debug = 1;
          break;

        case 'e':
          launch_editor = true;
          break;
		  
        case 'f':
          fullscreen = true;
          break;

        case 'g':
          if (sscanf(argp.get_argument().c_str(), "%dx%d", &screen_width, &screen_height) == 2)
            {
              std::cout << "Geometry: " << screen_width << "x" << screen_height << std::endl;
            }
          break;
		  
        case 'j':
          if (!from_string(argp.get_argument(), joystick_id)) {
            std::cout << "Error: Couldn't convert '" << argp.get_argument() << "' to joystick_id" 
                      << std::endl;
          }
          break;

        case 'h':
          argp.print_help();
          exit(EXIT_SUCCESS);
          break;

        case CL_CommandLine::REST_ARG:
          levelfile = argp.get_argument();
          break;
        }
    }
}

int 
WindstilleMain::main(int argc, char** argv)
{
  CL_ConsoleWindow console("Windstille Debug Window");
  console.redirect_stdio();

  // Init the path
  bindir  = CL_System::get_exe_path();
  libdir  = bindir + "../lib/";
  datadir = bindir + "../data/";

#ifndef WIN32
    char* home_c = getenv("HOME");
    if (home_c) 
      {
        std::string home = home_c; 
        home += "/.windstille";
        if (CL_Directory::create(home))
          std::cout << "Created " << home << std::endl;
        homedir = home + "/";
      }
    else
      {
        throw WindstilleError("Couldn't find environment variable HOME");
      }
#else
    homedir = "config/";
#endif
  
  try {
    parse_command_line(argc, argv);
    init_modules();

    for (int i = 0; i < 255; ++i)
      {
        CL_Display::clear(CL_Color(i, i, i));
        CL_Display::flip();
        CL_System::keep_alive();
        CL_System::sleep(20);
      }
    
    std::cout << "Detected " << CL_Joystick::get_device_count() << " joysticks" << std::endl;

    // FIXME:
    if (joystick_id != -1)
      new GamepadController(joystick_id);
    else
      new KeyboardController();
        
    if (!launch_editor && levelfile.empty())
      {
        std::cout << "Starting Menu" << std::endl;
        WindstilleMenu menu;
        menu.display();
      }
    else if (!launch_editor) // Launch Level
      {
        WindstilleGame game (levelfile);
        std::cout << "WindstilleMain: entering main-loop..." << std::endl;
        game.display ();
      }
    else
      {
        Editor editor;
        if (!levelfile.empty ())
          editor.load (levelfile);
        editor.run();
      }

    deinit_modules();

  } catch (CL_Error& error) {
    std::cout << "CL_Error: " << error.message << std::endl;
  } catch (std::exception& err) {
    std::cout << "std::exception: " << err.what() << std::endl;
  } catch (...) {
    std::cout << "Error catched something unknown?!" << std::endl;
  }

  return 0;
}

void
WindstilleMain::init_modules()
{
  scm_init_guile();
  SWIG_init();

  std::cout << "Loading Guile Code..." << std::endl;

  gh_eval_str("(display \"Guile: Enabling debugging...\\n\")"
              "(debug-enable 'debug)"
              "(debug-enable 'backtrace)"
              "(read-enable 'positions)");

  gh_define("*windstille-levelfile*",      gh_str02scm(levelfile.c_str()));
  gh_define("*windstille-datadir*",        gh_str02scm(datadir.c_str()));
  gh_define("*windstille-package-string*", gh_str02scm(PACKAGE_STRING));

  std::cout << "Loading Guile Code... done" << std::endl;

  CL_SetupCore::init();
  CL_SetupGL::init();
  CL_SetupDisplay::init();

  if (!sound_disabled)
    {
      CL_SetupSound::init();
      CL_SetupVorbis::init();
    }

  window = new CL_DisplayWindow(PACKAGE_STRING,
                                screen_width, screen_height, fullscreen, allow_resize);
  if (!sound_disabled)
    sound = new CL_SoundOutput(44100);

  resources =  new CL_ResourceManager();
  resources->add_resources(CL_ResourceManager(datadir + "tiles.xml", false));
  resources->add_resources(CL_ResourceManager(datadir + "windstille.xml", false));
  
  TileFactory::init();
  Fonts::init(); 
  MusicManager::init();
}

void
WindstilleMain::deinit_modules()
{
  MusicManager::deinit();
  Fonts::deinit();
  TileFactory::deinit();

  if (!sound_disabled)
    delete sound;
  
  delete window;

  if (!sound_disabled)
    {
      CL_SetupVorbis::init();
      CL_SetupSound::init();
    }

  CL_SetupDisplay::init();
  CL_SetupGL::init();
  CL_SetupCore::init(); 
}

/* EOF */
