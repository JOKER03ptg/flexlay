//  $Id: WindstilleGame.cxx,v 1.3 2003/08/06 17:16:19 grumbel Exp $
//
//  Pingus - A free Lemmings clone
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

#include <ClanLib/gl.h>

#include "GameWorld.hxx"
#include "GameObj.hxx"
//#include "GamepadController.hxx"
#include "KeyboardController.hxx"
#include "DeltaManager.hxx"
#include "Player.hxx"
#include "AnimationObj.hxx"
#include "TileMap.hxx"
#include "Dog.hxx"
#include "PowerUp.hxx"
#include "BonusFlyer.hxx"
#include "PlayerView.hxx"

#include "GuileGameObjFactory.hxx"
#include "WindstilleGame.hxx"

WindstilleGame::WindstilleGame (const std::string& arg_filename)
  : filename (arg_filename)
{
}

void
WindstilleGame::display ()
{ 
  DeltaManager delta_manager;
  
  Controller* controller1;
  Controller* controller2;

#if 0
  if (CL_Input::joysticks.size () >= 2)
    {
      controller1 = new GamepadController (1);
      controller2 = new GamepadController (0);
    }
  else if (CL_Input::joysticks.size () == 1)
    {
      controller1 = new GamepadController (0);
      controller2 = new KeyboardController ();
    }
  else
#endif
    {
      controller1 = new KeyboardController ();
      controller2 = new KeyboardController ();
    }

  Player player1 (controller1);
  Player player2 (controller2);

  player1.set_position (CL_Vector (100, 400));
  player2.set_position (CL_Vector (600, 500));

  player1.set_direction (WEST);
  player2.set_direction (EAST);

  std::cout << "Creating world" << std::endl;
  GameWorld world (filename);
  GameObj::set_world (&world);

  world.add (new Dog (CL_Vector (320, 200), WEST));
  world.add (new Dog (CL_Vector (320, 200), EAST));

  world.add (new ShildPowerUp (CL_Vector (420, 600)));
  world.add (new ShildPowerUp (CL_Vector (220, 1400)));
  world.add (new ShildPowerUp (CL_Vector (120, 1200)));
  world.add (new SpreadPowerUp (CL_Vector (120, 600)));

  world.add (new BonusFlyer (CL_Vector2 (100, 600)));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add_player (&player1);
  world.add_player (&player2);
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));
  world.add (GuileGameObjFactory::create ("scmdog"));

  world.add (GuileGameObjFactory::create ("nebular"));
  world.add (GuileGameObjFactory::create ("nebular"));
  world.add (GuileGameObjFactory::create ("nebular"));
  world.add (GuileGameObjFactory::create ("nebular"));
  world.add (GuileGameObjFactory::create ("nebular"));

  world.add (GuileGameObjFactory::create ("bounce"));
  world.add (GuileGameObjFactory::create ("bounce"));
  world.add (GuileGameObjFactory::create ("bounce"));
  world.add (GuileGameObjFactory::create ("bounce"));
  world.add (GuileGameObjFactory::create ("bounce"));
  world.add (GuileGameObjFactory::create ("bounce"));
  world.add (GuileGameObjFactory::create ("bounce"));

  PlayerView view (&player2);

  while (!CL_Keyboard::get_keycode (CL_KEY_ESCAPE))
    {
      float delta = delta_manager.getset ();
      CL_System::sleep (1);

      CL_Display::clear (CL_Color(0, 0, 127, 255));

      view.draw ();
      view.update (delta);

      world.update (delta);

      CL_Display::flip ();
	
      //world.add (new AnimationObj ("shoot/explosion", CL_Vector (rand ()% 800, rand ()%600)));

      CL_System::keep_alive ();
    } 
}


/* EOF */
